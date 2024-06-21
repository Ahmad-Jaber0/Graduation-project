from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import auth
from django.http import HttpResponse,JsonResponse, HttpResponseBadRequest,HttpResponseNotFound,HttpResponseRedirect

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
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from .models import User  # Import your custom User model

def Newlogin(request):
    if request.method == 'POST':
        userName = request.POST.get('userName')
        password = request.POST.get('password')
        
        user = authenticate(username=userName, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            return JsonResponse({'success': False, 'message': 'Invalid username or password'}, status=400)

    else:
        return render(request, 'login.html')

def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        FN = request.POST.get('first_name')
        LN = request.POST.get('last_name')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        phone_number = request.POST.get('phoneNumber')

        errors = {}

        if pass1 != pass2:
            errors['password_mismatch'] = 'Passwords do not match.'

        if User.objects.filter(username=uname).exists():
            errors['username_exists'] = 'Username already exists.'

        if User.objects.filter(email=email).exists():
            errors['email_exists'] = 'Email already exists.'

        if errors:
            return render(request, 'signup.html', {'errors': errors, 'form_data': request.POST})
        
        # If no errors, create the user
        my_user = User.objects.create_user(username=uname, email=email, first_name=FN, last_name=LN, password=pass1,phoneNumber=phone_number)
        my_user.save()

        # Authenticate and log in the user
        user = authenticate(username=uname, password=pass1)
        
        if user is not None:
            login(request, user)
            return redirect('info')

    return render(request, 'signup.html')


def info(request):
    return render(request,'recommender.html')

@login_required
def save_questionnaire(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        q1 = data.get('q1', '0')
        q1_2 = data.get('q1.2', '0')
        q2 = data.get('q2', '0')
        q3 = data.get('q3', '0')
        q4 = data.get('q4', '0')
        q5 = data.get('q5', '0')

        # Save questionnaire response
        questionnaire_response = QuestionnaireResponse(
            user=user,
            q1=q1,
            q1_2=q1_2,
            q2=q2,
            q3=q3,
            q4=q4,
            q5=q5
        )
        questionnaire_response.save()

        user_responses = QuestionnaireResponse.objects.get(user=request.user)

        courses = Course.objects.all()
        recommendation_matrix = []

        # Initialize recommendation matrix with zeros
        for course in courses:
            recommendation_matrix.append({
                'course': course,
                'q1': 0,
                'q2': 0,
                'q3': 0,
                'q4': 0,
                'q5': 0,
                'q1_2_adjusted': 0.0,
                'total_score': 0.0
            })

        # Define the weights for each question response to course attribute mapping
        weights = {
            'q1': 'front',
            'q2': 'back',
            'q3': 'basic',
            'q4': 'oop',
            'q5': 'algo',
        }

        # Calculate scores for each course
        for i, score_entry in enumerate(recommendation_matrix):
            course = score_entry['course']

            for question, attribute in weights.items():
                response_value = getattr(user_responses, question, '0')
                attribute_value = getattr(course, attribute, 0.0)
                weighted_score = float(response_value) * attribute_value
                recommendation_matrix[i][question] = weighted_score
                recommendation_matrix[i]['total_score'] += weighted_score

            provFront_value = getattr(course, 'provFront', 0.0)
            q1_2_value = getattr(user_responses, 'q1_2', '0')
            if float(q1_2_value) == float(provFront_value):
                recommendation_matrix[i]['q1_2_adjusted'] = float(q1_2_value)
                recommendation_matrix[i]['total_score'] += float(q1_2_value)

        max_score = -1
        max_score_course = None

        for entry in recommendation_matrix:
            if entry['total_score'] > max_score:
                max_score = entry['total_score']
                max_score_course = entry['course']

        if max_score_course:
            return JsonResponse({'message': f'go the course {max_score_course.name}'})
        else:
            return JsonResponse({'error': 'No course recommendation available.'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def LogoutPage(request): ###### Logout and go in the home page :)
    logout(request)
    return redirect('home')   
############################################

############### home page and profile ######################333
def home(request):
    courses = Course.objects.all()
    saved_courses = []

    if request.user.is_authenticated:
        saved_courses = SavedCourse.objects.filter(user=request.user).values_list('course_id', flat=True)
    
    return render(request, 'home.html', {
        'courses': courses,
        'saved_courses': saved_courses,
        'is_authenticated': request.user.is_authenticated,
    })

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

@login_required(login_url='login')
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
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
@login_required
def Dynamic(request):
    if request.method == 'POST':
        # Retrieve form data
        course_name = request.POST.get('Course-Name:')
        chapter_number = request.POST.get('Chapter-Number')
        topic_name = request.POST.get('textInput')
        topic_rank = request.POST.get('topicRank')
        if 'courseImage' in request.FILES:
            profile_image = request.FILES['courseImage']
        else:
            profile_image = 'profile_images/default.png'


        # Convert score inputs to float and divide by 100
        try:
            basic_score = float(request.POST.get('basicProgramming', '0')) / 100
            oop_score = float(request.POST.get('oop', '0')) / 100
            algo_score = float(request.POST.get('algorithms', '0')) / 100
            front_score = float(request.POST.get('frontend', '0')) / 100
            provFront_score = float(request.POST.get('frontendProficiency', '0')) / 100
            back_score = float(request.POST.get('backend', '0')) / 100
        except ValueError:
            basic_score = oop_score = algo_score = front_score = provFront_score = back_score = 0

        # Handle "other" inputs for course and chapter
        if course_name == 'other':
            course_name = request.POST.get('otherInput1')
        if chapter_number is None or chapter_number == 'other':
            chapter_number = f"Chapter {request.POST.get('otherInput2')}"

        # Check if course already exists, else create a new one
        course, created = Course.objects.get_or_create(
            name=course_name,
            defaults={
                'date': timezone.now(),
                'instructor': request.user.username,
               'profile_image': profile_image,
                'basic': basic_score,
                'oop': oop_score,
                'algo': algo_score,
                'front': front_score,
                'provFront': provFront_score,
                'back': back_score
            }
        )

        # Check if chapter already exists, else create a new one
        chapter, _ = Chapter.objects.get_or_create(course=course, name=chapter_number)

        # Check if topic already exists within the same chapter and course
        if Topic.objects.filter(topic_name=topic_name, course=course).exists():
            return JsonResponse({'error': 'Topic already exists within this chapter.'}, status=400)
        else:
            topic = Topic.objects.create(
                topic_name=topic_name,
                chapter=chapter,
                course=course,
                rank=topic_rank
            )

        return JsonResponse({'topic': {'id': topic.id, 'name': topic.topic_name, 'courseName': course.name}})

    # For GET requests, retrieve and pass existing courses and chapters to the form
    courses = Course.objects.all()
    chapters = Chapter.objects.all()
    return render(request, 'Form.html', {'courses': courses, 'chapters': chapters})

def dynamic_page(request): ##### Dynamic Html after fill the form then render the html to complete content course  :)

    topic_Name = request.GET.get('topic_Name')
    courseName=request.GET.get('course_name')
    course=get_object_or_404(Course,name=courseName)

    # Get the topic object based on the topic_id
    topic = get_object_or_404(Topic, topic_name=topic_Name,course=course)

    # Render the dynamic.html template with the topic data
    return render(request, 'dynamic.html', {'topic': topic, 'is_edit': False})
################################################################

########## API to get chapter and course #################
def fetch_chapters(request):####### Get specifc chapter to this course  :)
    course_name = request.GET.get("course")
    if course_name:
        chapters = Chapter.objects.filter(course__name=course_name).values_list("name", flat=True)
        return JsonResponse({"chapters": list(chapters)})
    return JsonResponse({"error": "Invalid request"})

def fetch_topics(request):
    course_name = request.GET.get('course')
    chapter_name = request.GET.get('chapter')

    if course_name and chapter_name:
        topics = Topic.objects.filter(course__name=course_name, chapter__name=chapter_name).values('id', 'topic_name')
        return JsonResponse({'topics': list(topics)})
    else:
        return JsonResponse({"error": "Invalid request"})
#############################################

######### Form Edit and delete Course ################
def Edit_course(request): ######## render Edit Form Course  :)
    course=Course.objects.all()
    return render(request,'Edit.html',{'courses':course})

def Del_course(request):####### render Delete Form Course   :)
    course=Course.objects.all() 
    return render(request,'Delete.html',{'courses':course})

def Del_Quiz(request):
    courses_with_quizzes = Course.objects.filter(quizquestion__isnull=False).distinct()
    return render(request, 'DeleteQuiz.html', {'courses': courses_with_quizzes})

def fetch_questions(request):
    course_name = request.GET.get('course')
    if course_name:
        questions = QuizQuestion.objects.filter(course__name=course_name).values('question_number')
        return JsonResponse({'questions': list(questions)})
    else:
        return JsonResponse({"error": "Invalid request"})

def delete_quiz(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')

        if not course_name:
            return JsonResponse({"error": "Missing course_name parameter"}, status=400)

        if request.POST.get('DeleteEntireQuiz'):
            QuizQuestion.objects.filter(course__name=course_name).delete()
        else:
            question_number = request.POST.get('question_number')
            if question_number:
                quiz_question = get_object_or_404(QuizQuestion, course__name=course_name, question_number=question_number)
                quiz_question.delete()

        return redirect('delete_quiz')  # Redirect to the delete quiz form

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
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


def get_dynamic_content(request):
    if request.method == 'POST':
        course_name = request.POST.get('Course-Name')
        chapter_number = request.POST.get('Chapter-Number')
        topic_id = request.POST.get('topicName')

        topic = Topic.objects.get(pk=topic_id)

        return render(request, 'dynamic.html', {'topic': topic, 'is_edit': True})

def update_code_html(request, topic_id):
    if request.method == 'POST':
        try:
            topic = get_object_or_404(Topic, pk=topic_id)
            data = json.loads(request.body)
            code_html = data.get('codeHtml', '')
            topic.code_html = code_html
            topic.save()
            return JsonResponse({'success': True})
        except Topic.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Topic not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@require_POST
@login_required
def save_course(request):
    course_id = request.POST.get('course_id')
    if not course_id:
        return JsonResponse({'success': False, 'message': 'No course_id provided'})

    course = get_object_or_404(Course, id=course_id)
    user = request.user

    try:
        saved = SavedCourse.objects.get(user=user, course=course)
        saved.delete()  # Remove the saved course
        return JsonResponse({'success': True, 'message': 'Course removed successfully'})
    except SavedCourse.DoesNotExist:
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
        print(request.POST.get('phone_number'))

        # Handle profile image upload
        if 'image' in request.FILES:
            user_profile.profile_image = request.FILES['image']

        # Update password if provided
        new_password = request.POST.get('password')
        if new_password:
            user_profile.set_password(new_password)
            update_session_auth_hash(request, user_profile)  # Update session with new password

        try:
            user_profile.save()
            messages.success(request, "Profile updated successfully.")
        except Exception as e:
            messages.error(request, f"Failed to update profile: {str(e)}")
        
        return redirect('profile')

    return render(request, 'profile.html')

##########################################################################

######### Dynamic page quiz and save the quiz ####################### -------> we need change here
def dynamic_quiz(request):
    course_name = request.GET.get('course')

    if not course_name:
        return HttpResponseBadRequest("Course name is required.")  # Return 400 if course name is missing

    try:
        course = get_object_or_404(Course, name__iexact=course_name)
        topics = Topic.objects.filter(course=course)  # Fetch the topics related to the course

        return render(request, 'EnterQuiz.html', {'topics': topics, 'course_name': course_name})  # Render the template with the topics
    except Course.DoesNotExist:
        return render(request, 'EnterQuiz.html', {'error': f'Course "{course_name}" does not exist.'})  # Handle course not found
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return render(request, 'EnterQuiz.html', {'error': 'An unexpected error occurred.'})

@csrf_exempt
def save_quiz(request):
    if request.method == "POST":
        try:
            course_name = request.POST.get('Course_name')
            question_number = request.POST.get('question_number')
            question_mark = request.POST.get('question_mark')
            question_topics = request.POST.getlist('question_topics')
            question_sections_count = int(request.POST.get('question_sections_count'))
            html_content = request.POST.get('html_content')
            correct_answers = request.POST.get('correct_answers[]')

            # Check if the question number already exists for the course
            course = Course.objects.get(name=course_name)
            if QuizQuestion.objects.filter(course=course, question_number=question_number).exists():
                return JsonResponse({'success': False, 'error_message': 'Question number already exists for this course.'})

            # Split the correct_answers string into a list
            correct_answers_list = correct_answers.split(',')

            # Ensure the correct_answers list has the expected number of items
            if len(correct_answers_list) < question_sections_count:
                raise ValueError("Not enough correct answers provided.")

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
                    correct_answer_text=correct_answers_list[i]
                )

                

            # Return success response with course_name
            return HttpResponseRedirect(f"{reverse('EnterQuiz')}?course={course_name}")

        except Course.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Course does not exist.'})
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

    # Get the current question number; if not provided, find the lowest question number
    try:
        current_question_number = int(request.GET.get('question_number', None))
    except (TypeError, ValueError):
        # If no specific question is requested, start with the first available question
        first_question = QuizQuestion.objects.filter(course=course).order_by('question_number').first()
        if first_question:
            current_question_number = first_question.question_number
        else:
            return HttpResponseNotFound("No questions available for this course")

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
    print(next_question)

    return render(request, 'QuestionPage.html', {
        'quiz': quiz_question,
        'next_question_number': next_question_number if next_question else None
    })

@csrf_exempt
def check_answer(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        quiz_id = request.POST.get('quiz_id')
        selected_answers = json.loads(request.POST.get('selected_answers', '{}'))
        is_skip = request.POST.get('is_skip') == 'true'

        try:
            quiz = get_object_or_404(QuizQuestion, id=quiz_id, course_id=course_id)
            sections = QuestionSection.objects.filter(question=quiz)

            results = {}
            if not is_skip:
                # Server-side validation: Ensure all sections are answered
                missing_sections = []
                for section in sections:
                    section_id = str(section.section_number)
                    if section_id not in selected_answers:
                        missing_sections.append(section_id)

                if missing_sections:
                    return JsonResponse({
                        'status': 'Error',
                        'message': 'Please answer all sections of the question.'
                    }, status=400)

            for section in sections:
                section_id = str(section.section_number)
                if is_skip:
                    is_correct = False  # Mark as incorrect if skipped
                    user_answer = None
                else:
                    user_answer = selected_answers.get(section_id)
                    is_correct = user_answer == section.correct_answer_text

                results[section_id] = {
                    'user_answer': user_answer,
                    'is_correct': is_correct,
                }
                # Save user's answer regardless of whether it's correct or not
                UserAnswer.objects.create(
                    user=request.user,
                    section=section,
                    is_correct=is_correct
                )

            # Check if the user has gotten all answers wrong across all questions in the course
            user_answers = UserAnswer.objects.filter(user=request.user, section__question__course=course)
            all_answers_incorrect = not user_answers.filter(is_correct=True).exists()

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
                # If no more questions, or all answers are incorrect, provide chapter recommendations
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

                if max_score == min_score:
                    normalized = np.zeros_like(chapter_scores)  # Avoid division by zero by setting all normalized scores to 0
                else:
                    normalized = (chapter_scores - min_score) / (max_score - min_score)

                total_row_sum = np.sum(row_sums)
                threshold = row_sums / total_row_sum

                # Redirect to Chapter 1 if all answers are incorrect
                if all_answers_incorrect:
                    chapter_url = reverse('course', kwargs={'course_name': course.name}) + '#1'
                    message = "You should review Chapter 1."
                    return JsonResponse({'status': 'Success', 'results': results, 'course_page_url': chapter_url, 'message': message})

                for i in range(len(threshold)):
                    if normalized[i] <= threshold[i]:
                        message = f"You should review Chapter {i+1}."
                        chapter_url = reverse('course', kwargs={'course_name': course.name}) + f'#{i+1}'
                        return JsonResponse({'status': 'Success', 'results': results, 'course_page_url': chapter_url, 'message': message})

        except QuizQuestion.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


##################################################