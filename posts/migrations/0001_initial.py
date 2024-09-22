# Generated by Django 5.1 on 2024-09-22 18:14

import ckeditor_uploader.fields
import django.core.validators
import django.db.models.deletion
import posts.models
import simple_history.models
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
            name='HistoricalPost',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('title_tag', models.CharField(max_length=100)),
                ('summary', models.CharField(default='lorem ipsum dolor sit amet consectetur adipisicing elit sed do', max_length=100)),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(blank=True, default=posts.models.get_lorem_ipsum_text, verbose_name='Text')),
                ('date_posted', models.DateTimeField(blank=True, editable=False)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('to_edit', 'To Edit'), ('to_publish', 'To Publish'), ('published', 'Published')], default='draft', max_length=20)),
                ('keywords', models.CharField(blank=True, max_length=100, null=True)),
                ('thumbnail', models.TextField(blank=True, max_length=100, null=True)),
                ('publish_start_date', models.DateTimeField(blank=True, null=True)),
                ('publish_end_date', models.DateTimeField(blank=True, null=True)),
                ('change_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('author', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(blank=True, db_constraint=False, default=posts.models.get_default_category, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='posts.category')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical post',
                'verbose_name_plural': 'historical posts',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('title_tag', models.CharField(max_length=100)),
                ('summary', models.CharField(default='lorem ipsum dolor sit amet consectetur adipisicing elit sed do', max_length=100)),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(blank=True, default=posts.models.get_lorem_ipsum_text, verbose_name='Text')),
                ('date_posted', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('to_edit', 'To Edit'), ('to_publish', 'To Publish'), ('published', 'Published')], default='draft', max_length=20)),
                ('keywords', models.CharField(blank=True, max_length=100, null=True)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='thumbnails/')),
                ('publish_start_date', models.DateTimeField(blank=True, null=True)),
                ('publish_end_date', models.DateTimeField(blank=True, null=True)),
                ('change_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(default=posts.models.get_default_category, on_delete=django.db.models.deletion.SET_DEFAULT, to='posts.category')),
            ],
            options={
                'permissions': [('can_publish', 'Can publish post')],
            },
        ),
    ]
