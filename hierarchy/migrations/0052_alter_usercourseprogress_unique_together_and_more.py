# Generated by Django 5.0.3 on 2024-06-14 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0051_usertopicprogress_usercourseprogress'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usercourseprogress',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='usertopicprogress',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='usercourseprogress',
            name='progress',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.RemoveField(
            model_name='usercourseprogress',
            name='last_accessed_topic',
        ),
    ]
