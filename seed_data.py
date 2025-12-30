#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Category, Post
from django.utils import timezone

admin = User.objects.get(username='admin')

tech, _ = Category.objects.get_or_create(
    slug='technologia',
    defaults={'name': 'Technologia'}
)
life, _ = Category.objects.get_or_create(
    slug='zycie',
    defaults={'name': 'Życie'}
)

Post.objects.get_or_create(
    slug='witaj-w-easy-blog',
    defaults={
        'title': 'Witaj w Easy Blog!',
        'author': admin,
        'body': 'To jest pierwszy wpis demonstracyjny w naszym systemie blogowym. Tutaj możesz publikować artykuły, zarządzać komentarzami i kategoryzować zawartość.',
        'category': tech,
        'status': 'published',
        'published': timezone.now()
    }
)

Post.objects.get_or_create(
    slug='jak-dodawac-wpisy',
    defaults={
        'title': 'Jak dodawać wpisy?',
        'author': admin,
        'body': 'Aby dodać nowy wpis, przejdź do panelu administracyjnego (/admin/), a następnie dodaj nowy post. Każdy wpis może mieć przypisaną kategorię i jest widoczny publicznie po zatwierdzeniu statusu "published".',
        'category': tech,
        'status': 'published',
        'published': timezone.now()
    }
)

Post.objects.get_or_create(
    slug='system-komentarzy',
    defaults={
        'title': 'System komentarzy',
        'author': admin,
        'body': 'Każdy wpis wspiera komentarze. Komentarze muszą być zatwierdzone przez administratora zanim pojawią się na stronie. Możesz zarządzać nimi w panelu admin.',
        'category': life,
        'status': 'published',
        'published': timezone.now()
    }
)

print("Default data created!")
