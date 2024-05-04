from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import F

class User(AbstractUser):

    ROLE_CHOICES = [
        ('Manager', 'Manager'),
        ('Team Leader', 'Team Leader'),
        ('Developer', 'Developer'),
    ]
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


class Course(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    instructor = models.CharField(max_length=255)
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
        unique_together = (('topic_name', 'chapter', 'course','rank'),)


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

