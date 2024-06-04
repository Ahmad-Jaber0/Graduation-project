from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import auth, messages
from django.http import HttpResponse,HttpResponseForbidden,JsonResponse
from django.contrib.auth import authenticate,login,logout,get_user_model,update_session_auth_hash
from .models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Min

def home(request):
    course=Course.objects.all()
    print('hi')
    return render(request, 'home.html',{'courses':course})

@login_required
def profile(request):
    return render(request,'profile.html')


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_profile = User.objects.get(username=request.user.username)
        user_profile.first_name = request.POST.get('first_name', '')
        user_profile.last_name = request.POST.get('last_name', '')
        user_profile.email = request.POST.get('email', '')

        if 'image' in request.FILES:
            user_profile.image = request.FILES['image']

        user_profile.save()

        new_password = request.POST.get('password')
        if new_password:
            user_profile.set_password(new_password)
            user_profile.save()
            update_session_auth_hash(request, user_profile)

        return redirect('profile')

    return redirect('profile')


def course(request, course_name):
    # Get the course object
    course = get_object_or_404(Course, name=course_name)

    # Get the first chapter in this course ordered by name
    first_chapter = Chapter.objects.filter(
        course=course).order_by('name').first()

    if first_chapter:
        # Get the first topic in the first chapter ordered by rank
        first_topic = Topic.objects.filter(
            chapter=first_chapter).order_by('rank').first()

        if first_topic:
            return redirect('course_detail', course_name=course_name, topic_name=first_topic.topic_name)


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


def dynamic_quiz(request):
    course = Course.objects.get(name='Python') 
    topics = Topic.objects.filter(course=course)

    return render(request, 'EnterQuiz.html', {'topics': topics})


@csrf_exempt
def save_quiz(request):
    if request.method == "POST":
        try:
            course_name = 'Python'
            question_number = request.POST.get('question_number')
            question_mark = request.POST.get('question_mark')
            question_topics = request.POST.getlist('question_topics')
            question_sections_count = int(request.POST.get('question_sections_count'))
            html_content = request.POST.get('html_content')
            correct_answers = request.POST.get('correct_answers[]')

            # Split the correct_answers string into a list
            correct_answers_list = correct_answers.split(',')

            print("Received correct answers:", correct_answers_list)

            # Ensure the correct_answers list has the expected number of items
            if len(correct_answers_list) < question_sections_count:
                raise ValueError("Not enough correct answers provided.")

            course = Course.objects.get(name=course_name)

            # Create a new QuizQuestion instance
            quiz_question = QuizQuestion(
                course=course,
                question_number=question_number,
                question_mark=question_mark,
                sections_count=question_sections_count,
                html_content=html_content
            )
            quiz_question.save()

            # Add topics to the QuizQuestion instance
            for topic_id in question_topics:
                topic = Topic.objects.get(id=topic_id)
                quiz_question.topics.add(topic)

            # Create QuestionSection instances and save options
            for i in range(question_sections_count):
                question_section = QuestionSection.objects.create(
                    question=quiz_question,
                    section_number=i + 1,
                    correct_answer_text=correct_answers_list[i]  # Correct field name
                )

                # Get the options for this section
                options = request.POST.getlist(f'question_section_{i + 1}_options')
                for option_text in options:
                    QuestionOption.objects.create(section=question_section, option_text=option_text, option_id=f'{i + 1}{options.index(option_text) + 1}')

            return redirect('EnterQuiz')

        except Exception as e:
            print("Error:", e)
            return redirect('EnterQuiz')  # Redirect to an appropriate error page or display an error message
    else:
        return redirect('EnterQuiz')


def quiz(request):
    quiz=QuizQuestion.objects.get(id=28)

    return render(request,'QuestionPage.html',{'quiz':quiz})



@csrf_exempt
def check_answer(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        quiz_id = request.POST.get('quiz_id')
        selected_answers = json.loads(request.POST.get('selected_answers', '{}'))

        try:
            quiz = QuizQuestion.objects.get(id=quiz_id, course_id=course_id)
            sections = QuestionSection.objects.filter(question=quiz)

            results = {}
            for section in sections:
                section_id = str(section.section_number)
                user_answer = selected_answers.get(section_id)
                is_correct = user_answer == section.correct_answer_text
                results[section_id] = {
                    'user_answer': user_answer,
                    'is_correct': is_correct,
                }
                # Save the user's answer
                UserAnswer.objects.create(
                    user=request.user,
                    section=section,
                    is_correct=is_correct
                )

            print(results)
            return JsonResponse({'status': 'Success', 'results': results})
        except QuizQuestion.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)