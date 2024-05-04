from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.http import HttpResponse,HttpResponseForbidden,JsonResponse
from django.contrib.auth import authenticate,login,logout,get_user_model
from .models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from django.utils import timezone

        
def home(request):
    return render(request, 'home.html')

@login_required
def course(request, course_name):
    template_name = f"C++ {course_name}.html"
        
    return render(request, template_name)




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
            chapter_number=f"Chapter{x}"

        print(course_name)    
        print(chapter_number)    

        # Check if course already exists, else create a new one
        course, created = Course.objects.get_or_create(
            name=course_name,
            defaults={'date': timezone.now(), 'instructor': request.user.username}
        )

        # Check if chapter already exists, else create a new one
        chapter, created = Chapter.objects.get_or_create(course=course, name=chapter_number)

        # Check if topic already exists within the same chapter and course
        if Topic.objects.filter(topic_name=topic_name, chapter=chapter, course=course,rank=topic_rank).exists():
            return JsonResponse({'error': 'Topic already exists within this chapter.'}, status=400)
        else:
            topic = Topic.objects.create(topic_name=topic_name, chapter=chapter, course=course,rank=topic_rank )


        return render(request, 'dynamic.html',{'topic':topic})

    return render(request, 'Form.html')


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

def course_detail(request, course_name, topic_id):
    course = Course.objects.get(name=course_name)
    chapters = Chapter.objects.filter(course=course)
    topics = Topic.objects.filter(course=course).order_by('chapter', 'rank')  # Order topics by chapter and rank
    topic = Topic.objects.get(pk=topic_id)

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


