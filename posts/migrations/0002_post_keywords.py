# Generated by Django 5.1 on 2024-09-01 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='keywords',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
