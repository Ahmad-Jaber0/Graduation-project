from django.contrib import admin

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ['username','first_name','last_name','email','role','id']

class CourseAdmin(admin.ModelAdmin):
    list_display = ['name','date','instructor','id']

class ChapterAdmin(admin.ModelAdmin):
    list_display = ['course','name','id']

class TopicAdmin(admin.ModelAdmin):
    list_display = ['topic_name','chapter','course','code_html','rank','id']




admin.site.register(User,UserAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(Chapter,ChapterAdmin)
admin.site.register(Topic,TopicAdmin)



