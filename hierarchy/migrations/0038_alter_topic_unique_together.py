# Generated by Django 5.0.4 on 2024-05-07 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0037_alter_topic_unique_together_topic_rank_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='topic',
            unique_together={('topic_name', 'course')},
        ),
    ]
