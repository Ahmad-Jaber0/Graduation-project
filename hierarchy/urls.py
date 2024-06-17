from django.urls import path,re_path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',views.home,name='home'),
    path('login/', views.login, name='login'), 
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
    #path('EnterQuiz/',views.dynamic_quiz,name='EnterQuiz'),
    re_path(r'^EnterQuiz/$', views.dynamic_quiz, name='EnterQuiz'),
    path('save_quiz/', views.save_quiz, name='save_quiz'),
    path('quiz/', views.quiz,name='quiz'),
    path('check_answer/', views.check_answer, name='check_answer'),
    path('form-edit/',views.Edit_course,name='edit'),
    path('update/', views.update_course_chapter_topic, name='update_course_chapter_topic'),
    path('form-Del/',views.Del_course,name='Del'),
    path('delete/', views.delete_course_chapter_topic, name='delete_course_chapter_topic'),
    path('save_course/', views.save_course, name='save_course'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)