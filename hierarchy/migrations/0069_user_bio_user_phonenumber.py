# Generated by Django 5.0.3 on 2024-06-19 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0068_alter_questionnaireresponse_q1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='phoneNumber',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
