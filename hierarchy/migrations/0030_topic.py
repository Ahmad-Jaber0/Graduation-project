# Generated by Django 5.0.4 on 2024-05-02 10:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0029_chapter'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic_name', models.CharField(max_length=255)),
                ('rank', models.IntegerField()),
                ('code_html', models.TextField()),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hierarchy.chapter')),
            ],
        ),
    ]
