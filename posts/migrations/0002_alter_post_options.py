# Generated by Django 5.1 on 2024-09-02 01:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'permissions': [('can_publish', 'Can Publish')]},
        ),
    ]
