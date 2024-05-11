from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import auth, messages
from django.http import HttpResponse,HttpResponseForbidden,JsonResponse
from django.contrib.auth import authenticate,login,logout,get_user_model,update_session_auth_hash
from .models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from django.utils import timezone

from django.db.models import Min

def home(request):
    course=Course.objects.all()
    return render(request, 'home.html',{'courses':course})

@login_required
def profile(request):
    return render(request,'profile.html')


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_profile=User.objects.get(username=request.user.username)
        user_profile.first_name = request.POST.get('first_name', '')
        user_profile.last_name = request.POST.get('last_name', '')
        user_profile.email = request.POST.get('email', '')
        #user_profile.bio = request.POST['bio']
        #user_profile.phone_number = request.POST['phone_number']
        user_profile.save()
        new_password = request.POST.get('password')
        if new_password:
            user_profile.set_password(new_password)
            user_profile.save()
            update_session_auth_hash(request, user_profile)
        return redirect('profile')
    return redirect('profile')


@login_required
def course(request, course_name):
    smallest_rank = Topic.objects.filter(course__name=course_name).aggregate(min_rank=Min('rank'))['min_rank']
    
    topic = Topic.objects.filter(course__name=course_name, rank=smallest_rank).first()  
    
    return redirect('course_detail', course_name=course_name, topic_name=topic.topic_name)


def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        FN = request.POST.get('first_name')
        LN = request.POST.get('last_name')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if User.objects.filter(username=uname).exists():

            return JsonResponse({'error': 'Username already exists.'}, status=400)
        
        
        elif User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'email already exists.'}, status=400)
        else:
            my_user = User.objects.create_user(username=uname, email=email, first_name=FN, last_name=LN, password=pass1)
            my_user.save()
            return JsonResponse({'success': 'User created successfully'})
            
    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        userName = request.POST.get('userName')
        password = request.POST.get('password')
        
        user = auth.authenticate(username=userName, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('home')

        else:
            return JsonResponse({'success': False, 'message': 'Invalid username or password'}, status=400)

    else:
        return render(request, 'login.html')


@login_required
def LogoutPage(request):
    logout(request)
    return redirect('home')   

def dynamic_page(request):

    topic_Name = request.GET.get('topic_Name')
    courseName=request.GET.get('course_name')
    print(courseName)

    course=get_object_or_404(Course,name=courseName)

    # Get the topic object based on the topic_id
    topic = get_object_or_404(Topic, topic_name=topic_Name,course=course)

    # Render the dynamic.html template with the topic data
    return render(request, 'dynamic.html', {'topic': topic})

@login_required
def Dynamic(request):
    if request.method == 'POST':
        course_name = request.POST.get('Course-Name:')
        chapter_number = request.POST.get('Chapter-Number')
        topic_name = request.POST.get('textInput')
        topic_rank = request.POST.get('topicRank')

        if course_name == 'other':
            course_name = request.POST.get('otherInput1')
        if chapter_number is None or chapter_number == 'other':
            x = request.POST.get('otherInput2')
            chapter_number = f"Chapter{x}"

        # Check if course already exists, else create a new one
        course, created = Course.objects.get_or_create(
            name=course_name,
            defaults={'date': timezone.now(), 'instructor': request.user.username}
        )

        # Check if chapter already exists, else create a new one
        chapter, created = Chapter.objects.get_or_create(course=course, name=chapter_number)

        # Check if topic already exists within the same chapter and course
        if Topic.objects.filter(topic_name=topic_name, course=course).exists():
            return JsonResponse({'error': 'Topic already exists within this chapter.'}, status=400)
        else:
            topic = Topic.objects.create(topic_name=topic_name, chapter=chapter, course=course, rank=topic_rank)

        return JsonResponse({'topic': {'id': topic.id,'name':topic.topic_name,'courseName':course.name}})

    course=Course.objects.all()
    chapter=Chapter.objects.all()

    return render(request, 'Form.html',{'course':course,'chapter':chapter}) 

def fetch_chapters(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        course_name = request.GET.get("course")
        if course_name:
            chapters = Chapter.objects.filter(course__name=course_name).values_list("name", flat=True)
            return JsonResponse({"chapters": list(chapters)})
    return JsonResponse({"error": "Invalid request"})


def fetch_topics(request):
    course_name = request.GET.get('course')
    chapter_number = request.GET.get('chapter')

    # Retrieve topics based on course name and chapter number
    topics = Topic.objects.filter(course__name=course_name, chapter__name=chapter_number).values('id', 'topic_name')

    return JsonResponse({'topics': list(topics)})


def update_code_html(request, topic_id):
    if request.method == 'POST':
        try:
            topic = Topic.objects.get(pk=topic_id)
            data = json.loads(request.body)
            code_html = data.get('codeHtml', '')
            topic.code_html = code_html
            topic.save()
            return JsonResponse({'success': True})
        except Topic.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Topic not found.'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

def course_detail(request, course_name, topic_name):
    course = Course.objects.get(name=course_name)
    chapters = Chapter.objects.filter(course=course)
    topics = Topic.objects.filter(course=course).order_by('chapter', 'rank')  # Order topics by chapter and rank
    topic = Topic.objects.get(course=course,topic_name=topic_name)

    previous_topic = None
    next_topic = None

    # Find previous and next topics within the same chapter
    for i, t in enumerate(topics):
        if t == topic:
            if i > 0:
                previous_topic = topics[i - 1]
            if i < len(topics) - 1:
                next_topic = topics[i + 1]
            break

    return render(request, 'base1.html', {'course1': course_name, 'chapters': chapters, 'topics': topics, 'top': topic, 'previous_top': previous_topic, 'next_top': next_topic})


