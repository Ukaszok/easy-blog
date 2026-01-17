#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Category, Post
from django.utils import timezone

if not User.objects.filter(username='admin').exists(): User.objects.create_superuser('admin', 'admin@example.com', '1234')
admin, created = User.objects.get_or_create(username='admin')

tech, _ = Category.objects.get_or_create(
    slug='technologia',
    defaults={'name': 'Technologia'}
)
life, _ = Category.objects.get_or_create(
    slug='zycie',
    defaults={'name': 'Życie'}
)

obj, created = Post.objects.get_or_create( slug='wweb', defaults={ 'title': 'Witaj w Easy Blog!', 'author': admin, 'body': 'To jest pierwszy wpis demonstracyjny...', 'category': tech, 'status': 'published', 'published': timezone.now() } )
print(created, obj)

print("Default data created!")
