# Generated by Django 5.0.4 on 2024-05-16 16:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0038_alter_topic_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_text', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_number', models.IntegerField()),
                ('correct_answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='correct_answer', to='hierarchy.option')),
            ],
        ),
        migrations.AddField(
            model_name='option',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hierarchy.questionsection'),
        ),
        migrations.CreateModel(
            name='QuizQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_number', models.IntegerField()),
                ('question_mark', models.IntegerField()),
                ('sections_count', models.IntegerField()),
                ('html_content', models.TextField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hierarchy.course')),
                ('topics', models.ManyToManyField(to='hierarchy.topic')),
            ],
        ),
        migrations.AddField(
            model_name='questionsection',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hierarchy.quizquestion'),
        ),
    ]
