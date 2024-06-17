from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import auth
from django.http import HttpResponse,JsonResponse, HttpResponseBadRequest,HttpResponseNotFound
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from .models import *
from django.contrib.auth.decorators import login_required
import json
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Min
from django.urls import reverse
import numpy as np
from django.views.decorators.http import require_POST

#################### auth ################################33
def SignupPage(request): ############## signipPage :)
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

def login(request): ######## loginPage after signup :)
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
def LogoutPage(request): ###### Logout and go in the home page :)
    logout(request)
    return redirect('home')   
############################################

############### home page and profile ######################333
def home(request): ############## present The Home page :)
    course=Course.objects.all()
    return render(request, 'home.html',{'courses':course})

@login_required
def profile(request): ############## present The profile page to the user after login :)
    user = request.user
    user_courses = UserCourseProgress.objects.filter(user=user)
    
    for user_course in user_courses:
        user_course.progress_percentage = user_course.get_progress_percentage()
    course=SavedCourse.objects.filter(user=user)
    course1=Course.objects.all()

    return render(request, 'profile.html', {'user_courses': user_courses,'courses':course,'course1':course1})
######################################################################

###################### Course Page #######################
def course(request, course_name): ##### in the page course when click the Open Course :)
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

@login_required
def course_detail(request, course_name, topic_name): ##### present the course Page :)
    course = get_object_or_404(Course, name=course_name)
    chapters = Chapter.objects.filter(course=course)
    topics = Topic.objects.filter(course=course).order_by('chapter', 'rank')
    topic = get_object_or_404(Topic, course=course, topic_name=topic_name)

    previous_topic = None
    next_topic = None

    for i, t in enumerate(topics):
        if t == topic:
            if i > 0:
                previous_topic = topics[i - 1]
            if i < len(topics) - 1:
                next_topic = topics[i + 1]
            break

    # Check if the course has any quiz questions
    has_quiz_questions = QuizQuestion.objects.filter(course=course).exists()

    # Check if the message has been shown for this course
    user_course_message, created = UserCourseMessage.objects.get_or_create(user=request.user, course=course)
    show_message = has_quiz_questions and not user_course_message.message_shown

    if request.user.is_authenticated:
        course_progress, _ = UserCourseProgress.objects.get_or_create(user=request.user, course=course)
        topic_progress, _ = UserTopicProgress.objects.get_or_create(user=request.user, topic=topic)

        if not topic_progress.completed:
            topic_progress.completed = True
            topic_progress.save()

            # Update course progress after marking a topic as completed
            course_progress.update_progress()

        completed_topic_ids = UserTopicProgress.objects.filter(
            user=request.user,
            topic__course=course,
            completed=True
        ).values_list('topic_id', flat=True)
    else:
        completed_topic_ids = []

    return render(request, 'base1.html', {
        'course1': course_name,
        'chapters': chapters,
        'topics': topics,
        'top': topic,
        'previous_top': previous_topic,
        'next_top': next_topic,
        'progress_percentage': course_progress.get_progress_percentage() if request.user.is_authenticated else 0,
        'completed_topic_ids': completed_topic_ids,
        'show_message': show_message,  # Pass the show_message flag to the template
        'course_name': course_name
    })
########################################################

########## Dynamic page and form to add course ##################
@login_required
def Dynamic(request): ######## this is dynamic if the request is get build the Form html to add course if Post then save the info of this course  :)
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

def dynamic_page(request): ##### Dynamic Html after fill the form then render the html to complete content course  :)

    topic_Name = request.GET.get('topic_Name')
    courseName=request.GET.get('course_name')
    course=get_object_or_404(Course,name=courseName)

    # Get the topic object based on the topic_id
    topic = get_object_or_404(Topic, topic_name=topic_Name,course=course)

    # Render the dynamic.html template with the topic data
    return render(request, 'dynamic.html', {'topic': topic})
################################################################

########## API to get chapter and course #################
def fetch_chapters(request):####### Get specifc chapter to this course  :)
    if request.method == "GET" :
        course_name = request.GET.get("course")
        print(course_name)
        if course_name:
            chapters = Chapter.objects.filter(course__name=course_name).values_list("name", flat=True)
            return JsonResponse({"chapters": list(chapters)})
    return JsonResponse({"error": "Invalid request"})

def fetch_topics(request):#######3 Get specifc Topics of this chapter and this course   :)
    course_name = request.GET.get('course')
    chapter_number = request.GET.get('chapter')

    # Retrieve topics based on course name and chapter number
    topics = Topic.objects.filter(course__name=course_name, chapter__name=chapter_number).values('id', 'topic_name')

    return JsonResponse({'topics': list(topics)})
#############################################

######### Form Edit and delete Course ################
def Edit_course(request): ######## render Edit Form Course  :)
    course=Course.objects.all()
    return render(request,'Edit.html',{'courses':course})

def Del_course(request):####### render Delete Form Course   :)
    course=Course.objects.all() 
    return render(request,'Delete.html',{'courses':course})
############################################

####### change the html or name of course topic ...ect and update code html in dynamic ###############333
def delete_course_chapter_topic(request): ######## after Delete.html then remove course or chapter or topic :)
    if request.method == 'POST':
        course_name = request.POST.get('Course-Name')
        chapter_name = request.POST.get('Chapter-Number')
        topic_id = request.POST.get('topicName')

        if request.POST.get('DeleteEntireCourse'):
            course = get_object_or_404(Course, name=course_name)
            course.delete()
        elif request.POST.get('DeleteEntireChapter'):
            chapter = get_object_or_404(Chapter, course__name=course_name, name=chapter_name)
            chapter.delete()
        else:
            topic = get_object_or_404(Topic, id=topic_id, chapter__name=chapter_name, chapter__course__name=course_name)
            topic.delete()

        return redirect('profile')


def update_course_chapter_topic(request):######3 Edit Course ---> Change here :)
    if request.method == 'POST':
        button_clicked = request.POST.get('button_clicked')

        print(button_clicked)
        print('jjj')
        

        course_name = request.POST.get('Course-Name')
        chapter_name = request.POST.get('Chapter-Number')
        topic_id = request.POST.get('topicName')
        

        if not (course_name and chapter_name and topic_id):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        try:
            course = get_object_or_404(Course, name=course_name)
            chapter = get_object_or_404(Chapter, course=course, name=chapter_name)
            topic = get_object_or_404(Topic, id=topic_id, chapter=chapter)
            return render(request, 'dynamic.html', {'topic': topic})

            if request.POST.get('courseNewName'):
                new_course_name = request.POST.get('New-Course-Name')
                course.name = new_course_name
                course.save()

            if request.POST.get('chapterNewNumber'):
                new_chapter_name = request.POST.get('New-Chapter-Number')
                chapter.name = new_chapter_name
                chapter.save()

            if request.POST.get('topicNewName'):
                new_topic_name = request.POST.get('New-Topic-Name')
                topic.topic_name = new_topic_name
                topic.save()

            if request.POST.get('topicNewOrder'):
                new_topic_order = request.POST.get('New-Topic-Order')
                topic.rank = new_topic_order
                topic.save()

            if button_clicked == 'saveEditButton':
                print('jojo')
                return render(request, 'dynamic.html', {'topic': topic})

            return redirect('profile')

        except Exception as e:
            return JsonResponse({'error': 'An error occurred while processing the form submission'}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)


def update_code_html(request, topic_id):  ### after dynamic.html save the contet html of the topic :)
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

@require_POST
def save_course(request):######### save course when click in the image saved course and present in the profile :)
    course_id = request.POST.get('course_id')
    if not course_id:
        return JsonResponse({'success': False, 'message': 'No course_id provided'})

    course = get_object_or_404(Course, id=course_id)
    user = request.user  # Assuming user is authenticated

    try:
        # Check if the course is already saved by the user
        saved = SavedCourse.objects.get(user=user, course=course)
        saved.delete()  # Remove the saved course
        return JsonResponse({'success': True, 'message': 'Course removed successfully'})##########3 remmeber change this text
    except SavedCourse.DoesNotExist:
        # Create a new SavedCourse instance for the user
        saved_course = SavedCourse(user=user, course=course)
        saved_course.save()
        return JsonResponse({'success': True, 'message': 'Course saved successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

from django.contrib import messages
@login_required
def update_profile(request):
    if request.method == 'POST':
        user_profile = request.user

        # Update basic profile information
        user_profile.first_name = request.POST.get('first_name', '')
        user_profile.last_name = request.POST.get('last_name', '')
        user_profile.email = request.POST.get('email', '')
        user_profile.bio = request.POST.get('bio', '')
        user_profile.phone_number = request.POST.get('phone_number', '')

        # Handle profile image upload
        if 'image' in request.FILES:
            user_profile.profile_image = request.FILES['image']

        # Update password if provided
        new_password = request.POST.get('password')
        if new_password:
            user_profile.set_password(new_password)
            update_session_auth_hash(request, user_profile)  # Update session with new password

        try:
            user_profile.full_clean()  # Validate fields (optional)
            user_profile.save()
            messages.success(request, "Profile updated successfully.")
        except Exception as e:
            messages.error(request, f"Failed to update profile: {str(e)}")
        
        return redirect('profile')

    return render(request, 'profile.html')

##########################################################################

######### Dynamic page quiz and save the quiz ####################### -------> we need change here
from django.db.models import Q
def dynamic_quiz(request, course=None): ### render the EnterQuiz.html and show the form to this quiz :)
    course_name = request.GET.get('course')

    if not course and not course_name:
        return HttpResponseBadRequest("Course name is required.")  # Return 400 if course name is missing

    if not course_name:
        course1 = get_object_or_404(Course, Q(name__iexact=course))  # Return 400 if course name is missing
    else:
        course1 = get_object_or_404(Course, Q(name__iexact=course_name))

    try:
        topics = Topic.objects.filter(course=course1)  # Fetch the topics related to the course

        return render(request, 'EnterQuiz.html', {'topics': topics, 'course_name': course1})  # Render the template with the topics
    except Course.DoesNotExist:
        return render(request, 'EnterQuiz.html', {'error': f'Course "{course_name}" does not exist.'})  # Handle course not found
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return render(request, 'EnterQuiz.html', {'error': 'An unexpected error occurred.'})
        

@csrf_exempt
def save_quiz(request): ##### save this quiz after add   :)
    if request.method == "POST":
        try:
            course_name = request.POST.get('Course_name')
            question_number = request.POST.get('question_number')
            question_mark = request.POST.get('question_mark')
            question_topics = request.POST.getlist('question_topics')
            question_sections_count = int(request.POST.get('question_sections_count'))
            html_content = request.POST.get('html_content')
            correct_answers = request.POST.get('correct_answers[]')

            # Split the correct_answers string into a list
            correct_answers_list = correct_answers.split(',')

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
            # Return success response with course_name
            return JsonResponse({'success': True, 'course_name': course_name})

        except Exception as e:
            print("Error:", e)
            return JsonResponse({'success': False, 'error_message': 'Error saving quiz'})

    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})
########################################################

################ Page Quastion and return the number of chapter ---> Recomend 1 
import urllib.parse
@login_required
def quiz(request):
    # Get and decode the course name
    course_name = request.GET.get('course')
    if not course_name:
        return HttpResponseNotFound("Course name not provided")

    decoded_course_name = urllib.parse.unquote(course_name)  # Decode URL-encoded course name

    # Fetch the course using the decoded course name
    course = get_object_or_404(Course, name=decoded_course_name)

    # Get the current question number, default to 1 if not provided
    current_question_number = int(request.GET.get('question_number', 1))

    try:
        # Get the current quiz question
        quiz_question = QuizQuestion.objects.get(course=course, question_number=current_question_number)
    except QuizQuestion.DoesNotExist:
        return HttpResponseNotFound("Question not found")

    # Mark the message as shown for this course
    user_course_message, created = UserCourseMessage.objects.get_or_create(user=request.user, course=course)
    if not user_course_message.message_shown:
        user_course_message.message_shown = True
        user_course_message.save()

    # Determine the next question number
    next_question_number = current_question_number + 1
    next_question = QuizQuestion.objects.filter(course=course, question_number=next_question_number).first()

    return render(request, 'QuestionPage.html', {
        'quiz': quiz_question,
        'next_question_number': next_question_number if next_question else None
    })

@csrf_exempt
def check_answer(request):
    if request.method == 'POST':
        # Get course and quiz IDs from POST data
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        quiz_id = request.POST.get('quiz_id')
        selected_answers = json.loads(request.POST.get('selected_answers', '{}'))

        try:
            # Get the quiz question
            quiz = get_object_or_404(QuizQuestion, id=quiz_id, course_id=course_id)
            sections = QuestionSection.objects.filter(question=quiz)

            # Evaluate the user's answers
            results = {}
            for section in sections:
                section_id = str(section.section_number)
                user_answer = selected_answers.get(section_id)
                is_correct = user_answer == section.correct_answer_text
                results[section_id] = {
                    'user_answer': user_answer,
                    'is_correct': is_correct,
                }
                UserAnswer.objects.create(
                    user=request.user,
                    section=section,
                    is_correct=is_correct
                )

            # Find the next question
            next_question = QuizQuestion.objects.filter(
                course_id=course_id,
                question_number__gt=quiz.question_number
            ).order_by('question_number').first()

            if next_question:
                next_question_url = request.build_absolute_uri(
                    reverse('quiz') + f'?course={urllib.parse.quote(course.name)}&question_number={next_question.question_number}'
                )
                return JsonResponse({'status': 'Success', 'results': results, 'next_question_url': next_question_url})
            else:
                # Calculate chapter recommendations
                chapters = Chapter.objects.filter(course=course).order_by('id')
                questions = QuizQuestion.objects.filter(course=course).order_by('question_number')

                num_chapters = chapters.count()
                num_questions = questions.count()

                # Initialize the matrix
                matrix = np.zeros((num_chapters, num_questions), dtype=int)
                chapter_index_map = {chapter.id: idx for idx, chapter in enumerate(chapters)}
                row_sums = np.zeros(num_chapters, dtype=int)

                for question_idx, question in enumerate(questions):
                    topics = question.topics.all()
                    for topic in topics:
                        chapter_id = topic.chapter_id
                        if chapter_id in chapter_index_map:
                            chapter_idx = chapter_index_map[chapter_id]
                            matrix[chapter_idx][question_idx] += 1

                # Compute row sums and scores
                for chapter_idx in range(num_chapters):
                    row_sums[chapter_idx] = np.sum(matrix[chapter_idx])

                scores_array = []
                for question in questions:
                    sections = QuestionSection.objects.filter(question=question)
                    num_sections = sections.count()

                    correct_answers = UserAnswer.objects.filter(user=request.user, section__in=sections, is_correct=True).count()
                    score_fraction = correct_answers / num_sections if num_sections > 0 else 0
                    scores_array.append(score_fraction)

                scores_array = np.array(scores_array)
                chapter_scores = np.dot(matrix, scores_array)

                min_score = np.min(chapter_scores)
                max_score = np.max(chapter_scores)
                normalized = (chapter_scores - min_score) / (max_score - min_score)

                total_row_sum = np.sum(row_sums)
                threshold = row_sums / total_row_sum

                print(threshold)
                print(normalized)

                for i in range(len(threshold)):
                    if normalized[i] <= threshold[i]:
                        message = f"You should review Chapter {i+1}."############# change her
                        chapter_url = reverse('course', kwargs={'course_name': course.name}) + f'#{i+1}'
                        return JsonResponse({'status': 'Success', 'results': results, 'course_page_url': chapter_url, 'message': message})

        except QuizQuestion.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


##################################################