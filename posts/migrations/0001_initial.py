# Generated by Django 5.1 on 2024-09-02 08:39

import django.core.validators
import django.db.models.deletion
import django_ckeditor_5.fields
import posts.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(default='lorem ipsum dolor sit amet consectetur adipisicing elit sed do', max_length=100)),
                ('alias', models.CharField(default='', max_length=2)),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('kind', models.CharField(choices=[('public', 'Public'), ('free', 'Free'), ('premium', 'Premium')], default='free', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('title_tag', models.CharField(max_length=100)),
                ('summary', models.CharField(default='lorem ipsum dolor sit amet consectetur adipisicing elit sed do', max_length=100)),
                ('body', django_ckeditor_5.fields.CKEditor5Field(blank=True, default=posts.models.get_lorem_ipsum_text, verbose_name='Text')),
                ('date_posted', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('to_edit', 'To Edit'), ('to_publish', 'To Publish'), ('published', 'Published')], default='draft', max_length=20)),
                ('keywords', models.CharField(blank=True, max_length=100, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(default=posts.models.get_default_category, on_delete=django.db.models.deletion.SET_DEFAULT, to='posts.category')),
            ],
            options={
                'permissions': [('can_publish', 'Can publish post')],
            },
        ),
    ]
