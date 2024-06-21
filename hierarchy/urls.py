from django.urls import path,re_path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',views.home,name='home'),
    path('login/', views.Newlogin, name='login'), 
    path('signup/', views.SignupPage, name='signup'),
    path('logout/', views.LogoutPage, name='logout_page'),
    path('course/<str:course_name>/', views.course, name='course'),
    path('form/',views.Dynamic,name='form'),
    path('update_code_html/<int:topic_id>/', views.update_code_html, name='update_code_html'),
    path('<str:course_name>/<path:topic_name>/', views.course_detail, name='course_detail'),
    path('dynamic_page/', views.dynamic_page, name='dynamic_page'),
    path('fetch_chapters/', views.fetch_chapters, name='fetch_chapters'),
    path('fetch_topics/', views.fetch_topics, name='fetch_topics'),
    path('profile/',views.profile,name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    re_path(r'^EnterQuiz/$', views.dynamic_quiz, name='EnterQuiz'),
    path('save_quiz/', views.save_quiz, name='save_quiz'),
    path('quiz/', views.quiz,name='quiz'),
    path('check_answer/', views.check_answer, name='check_answer'),
    path('form-edit/',views.Edit_course,name='edit'),
    path('dynamic/', views.get_dynamic_content, name='dynamic_content'),
    path('form-Del/',views.Del_course,name='Del'),
    path('delete/', views.delete_course_chapter_topic, name='delete_course_chapter_topic'),
    path('save_course/', views.save_course, name='save_course'),
    path('info/',views.info,name='info'),
    path('save/',views.save_questionnaire,name='save_questionnaire'),
    path('delete_quiz/', views.Del_Quiz, name='delete_quiz'),
    path('fetch_questions/', views.fetch_questions, name='fetch_questions'),
    path('delete_quiz_post/', views.delete_quiz, name='delete_quiz_post'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)