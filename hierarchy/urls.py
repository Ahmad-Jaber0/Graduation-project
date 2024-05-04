from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('',views.home,name='home'),
    path('login/', views.login, name='login'), 
    path('signup/', views.SignupPage, name='signup'),
    path('logout/', views.LogoutPage, name='logout_page'),
    path('course/<str:course_name>/', views.course, name='course'),
    path('form/',views.Dynamic,name='form'),
    path('update_code_html/<int:topic_id>/', views.update_code_html, name='update_code_html'),
    path('<str:course_name>/<int:topic_id>/', views.course_detail, name='course_detail'),
] 