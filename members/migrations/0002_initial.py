# Generated by Django 5.1 on 2024-10-03 12:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('members', '0001_initial'),
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='purchased_categories',
            field=models.ManyToManyField(blank=True, related_name='purchased_members', to='posts.category'),
        ),
        migrations.AddField(
            model_name='member',
            name='suscribed_categories',
            field=models.ManyToManyField(blank=True, related_name='suscribed_members', to='posts.category'),
        ),
        migrations.AddField(
            model_name='member',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='notification',
            name='notifications',
            field=models.ManyToManyField(blank=True, related_name='notificaciones', to='posts.category'),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
