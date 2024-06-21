from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import F

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Developer', 'Developer'),
    ]
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,default='Developer')
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)  # Assuming phone numbers can include country code
    bio = models.TextField(blank=True)

class QuestionnaireResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    q1 = models.CharField(max_length=4, null=True, blank=True,default=0)
    q1_2 = models.CharField(max_length=4, null=True, blank=True,default=0)
    q2 = models.CharField(max_length=4, null=True, blank=True,default=0)
    q3 = models.CharField(max_length=4, null=True, blank=True,default=0)
    q4 = models.CharField(max_length=4, null=True, blank=True,default=0)
    q5 = models.CharField(max_length=4, null=True, blank=True,default=0)


class Course(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    instructor = models.CharField(max_length=255)
    check_boolean = models.BooleanField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')
    basic = models.FloatField(default=0.0)
    oop = models.FloatField(default=0.0)
    algo = models.FloatField(default=0.0)
    front = models.FloatField(default=0.0)
    provFront = models.FloatField(default=0.0)
    back = models.FloatField(default=0.0)
    
    def __str__(self):
        return self.name  

class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name    
    class Meta:
        unique_together = (('course', 'name'),)

class Topic(models.Model):
    topic_name = models.CharField(max_length=255)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Add this field
    code_html = models.TextField(null=True, blank=True)
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.topic_name

    class Meta:
        unique_together = (('topic_name', 'course'),)

class UserTopicProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.topic.topic_name}"

class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_accessed_topic = models.ForeignKey(UserTopicProgress, null=True, blank=True, on_delete=models.SET_NULL, related_name='last_accessed')

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"

    def update_progress(self):
        total_topics = Topic.objects.filter(course=self.course).count()
        completed_topics = UserTopicProgress.objects.filter(user=self.user, topic__course=self.course, completed=True).count()
        self.progress = (completed_topics / total_topics) * 100 if total_topics > 0 else 0
        self.save()

    def get_progress_percentage(self):
        return f"{self.progress:.2f}"

    

class SavedCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"
    


class UserCourseMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    message_shown = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.course.name} - {'Shown' if self.message_shown else 'Not Shown'}"


@receiver(pre_save, sender=Topic)
def update_topic_ranks(sender, instance, **kwargs):
    if instance.pk:  # If the topic already exists (i.e., it's being updated)
        # Get the original instance from the database
        original_instance = Topic.objects.get(pk=instance.pk)

        # Check if the chapter and rank of the topic have changed
        if original_instance.chapter != instance.chapter or original_instance.rank != instance.rank:
            # Decrement the rank of existing topics with rank greater than the new rank
            Topic.objects.filter(chapter=instance.chapter, rank__gt=instance.rank).update(rank=models.F('rank') - 1)

            # Increment the rank of existing topics with rank greater than or equal to the new rank
            Topic.objects.filter(chapter=instance.chapter, rank__gte=instance.rank).exclude(pk=instance.pk).update(rank=models.F('rank') + 1)
    else:  # If it's a new topic being created
        # Check if a topic with the same chapter and rank already exists
        existing_topic = Topic.objects.filter(chapter=instance.chapter, rank=instance.rank).first()
        if existing_topic:
            # Increment the rank of existing topics with rank greater than or equal to the new rank
            Topic.objects.filter(chapter=instance.chapter, rank__gte=instance.rank).update(rank=models.F('rank') + 1)
        else:
            # Increment the rank of existing topics with rank greater than the new rank
            Topic.objects.filter(chapter=instance.chapter, rank__gt=instance.rank).update(rank=models.F('rank') + 1)

class QuizQuestion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question_number = models.IntegerField()
    question_mark = models.IntegerField()
    topics = models.ManyToManyField('Topic')
    sections_count = models.IntegerField()
    html_content = models.TextField(null=True)  # Field to store HTML content of the question

    def __str__(self):
        return f"Question {self.question_number} - Course: {self.course.name}"
    class Meta:
        unique_together = (('course', 'question_number'),)

class QuestionSection(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='sections')
    section_number = models.IntegerField()
    correct_answer_text = models.CharField(null=True,max_length=255)  # Field to store the text of the correct answer

    def __str__(self):
        return f"Section {self.section_number} of Question {self.question.question_number}"
    class Meta:
        unique_together = (('question', 'section_number'),)


class QuestionOption(models.Model):
    section = models.ForeignKey(QuestionSection, on_delete=models.CASCADE)
    option_text = models.TextField()  # Store the actual option content
    option_id = models.CharField(max_length=255)  # Reference ID used in the frontend

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    section = models.ForeignKey(QuestionSection, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.user.username}'s answer for Section {self.section.section_number} - Correct: {self.is_correct}"