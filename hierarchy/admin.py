from django.contrib import admin
from .models import *

admin.site.site_header="LoomingCode"
admin.site.site_title="LoomingCode"




class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'role','profile_image','phoneNumber','id']
    list_editable=['role']
    search_fields=['username']
    list_filter=['role']

class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display=['user','q1','q1_2','q3','q4','q5']

class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'instructor', 'id','check_boolean','front','provFront','back','basic','oop','algo']

class ChapterAdmin(admin.ModelAdmin):
    list_display = ['course', 'name', 'id']

class TopicAdmin(admin.ModelAdmin):
    list_display = ['topic_name', 'chapter', 'course', 'code_html', 'rank', 'id']


class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['course', 'question_number', 'question_mark', 'display_topics', 'sections_count', 'html_content', 'id']

    def display_topics(self, obj):
        return ", ".join([topic.topic_name for topic in obj.topics.all()])


class QuestionSectionAdmin(admin.ModelAdmin):
    list_display = ['question', 'section_number', 'correct_answer_text', 'id']


class UserAnswerAdmin(admin.ModelAdmin):
    list_display=['user','section','is_correct','id']


class QuestionOptionAdmin(admin.ModelAdmin):
    list_display=['section','option_text','option_id']

class UserTopicProgressAmin(admin.ModelAdmin):
    list_display=['user','topic','completed']

class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display=['user','course','progress']

class UserCourseMessageAdmin(admin.ModelAdmin):
    list_display=['user','course','message_shown']

admin.site.register(User, UserAdmin)
admin.site.register(QuestionnaireResponse,QuestionnaireResponseAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(QuizQuestion, QuizQuestionAdmin)
admin.site.register(QuestionSection, QuestionSectionAdmin)
admin.site.register(UserAnswer,UserAnswerAdmin)
admin.site.register(QuestionOption,QuestionOptionAdmin)

admin.site.register(UserTopicProgress,UserTopicProgressAmin)
admin.site.register(UserCourseProgress,UserCourseProgressAdmin)
admin.site.register(UserCourseMessage,UserCourseMessageAdmin)

