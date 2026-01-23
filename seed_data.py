#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Category, Post, Tag, Comment
from django.utils import timezone
from django.utils.text import slugify

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
sport, _ = Category.objects.get_or_create(
    slug='sport',
    defaults={'name': 'Sport'}
)
culture, _ = Category.objects.get_or_create(
    slug='kultura',
    defaults={'name': 'Kultura'}
)
travel, _ = Category.objects.get_or_create(
    slug='podroze',
    defaults={'name': 'Podróże'}
)
cooking, _ = Category.objects.get_or_create(
    slug='gotowanie',
    defaults={'name': 'Gotowanie'}
)

# Create tags
tag_python, _ = Tag.objects.get_or_create(name='Python', defaults={'slug': slugify('Python')})
tag_django, _ = Tag.objects.get_or_create(name='Django', defaults={'slug': slugify('Django')})
tag_webdev, _ = Tag.objects.get_or_create(name='Web Development', defaults={'slug': slugify('Web Development')})
tag_health, _ = Tag.objects.get_or_create(name='Zdrowie', defaults={'slug': slugify('Zdrowie')})
tag_fitness, _ = Tag.objects.get_or_create(name='Fitness', defaults={'slug': slugify('Fitness')})
tag_recipe, _ = Tag.objects.get_or_create(name='Przepis', defaults={'slug': slugify('Przepis')})
tag_dessert, _ = Tag.objects.get_or_create(name='Deser', defaults={'slug': slugify('Deser')})
tag_vacation, _ = Tag.objects.get_or_create(name='Wakacje', defaults={'slug': slugify('Wakacje')})
tag_europe, _ = Tag.objects.get_or_create(name='Europa', defaults={'slug': slugify('Europa')})
tag_book, _ = Tag.objects.get_or_create(name='Książka', defaults={'slug': slugify('Książka')})
tag_movie, _ = Tag.objects.get_or_create(name='Film', defaults={'slug': slugify('Film')})

# Create test user
testuser, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'testuser@example.com',
        'first_name': 'Jan',
        'last_name': 'Kowalski'
    }
)
if created:
    testuser.set_password('test123')
    testuser.save()
    print(f"Created test user: {testuser.username}")

# Create posts
obj, created = Post.objects.get_or_create(
    slug='wweb',
    defaults={
        'title': 'Witaj w Easy Blog!',
        'author': admin,
        'body': 'To jest pierwszy wpis demonstracyjny. Ten blog został stworzony w Django i oferuje wiele funkcji takich jak kategorie, tagi, komentarze i system moderacji.',
        'category': tech,
        'status': 'published',
        'published': timezone.now()
    }
)
if created:
    obj.tags.add(tag_python, tag_django, tag_webdev)
    print(f"Created post: {obj.title}")

post2, created = Post.objects.get_or_create(
    slug='django-tutorial',
    defaults={
        'title': 'Wprowadzenie do Django',
        'author': admin,
        'body': 'Django to potężny framework webowy napisany w Pythonie. W tym poście poznasz podstawy Django, modele, widoki i szablony. Django ułatwia tworzenie aplikacji webowych dzięki swojej architekturze MVC.',
        'category': tech,
        'status': 'published',
        'published': timezone.now()
    }
)
if created:
    post2.tags.add(tag_python, tag_django)
    print(f"Created post: {post2.title}")

post3, created = Post.objects.get_or_create(
    slug='zdrowy-tryb-zycia',
    defaults={
        'title': 'Zdrowy tryb życia - porady',
        'author': admin,
        'body': 'Zdrowy tryb życia to klucz do dobrego samopoczucia. W tym poście znajdziesz praktyczne porady dotyczące diety, ćwiczeń i równowagi między pracą a życiem prywatnym. Pamiętaj, że małe zmiany mogą przynieść duże efekty!',
        'category': sport,
        'status': 'published',
        'published': timezone.now()
    }
)
if created:
    post3.tags.add(tag_health, tag_fitness)
    print(f"Created post: {post3.title}")

post4, created = Post.objects.get_or_create(
    slug='ciasto-czekoladowe',
    defaults={
        'title': 'Przepis na ciasto czekoladowe',
        'author': testuser,
        'body': 'Dziś podzielę się z Wami przepisem na pyszne ciasto czekoladowe. To prosty i szybki przepis, który zawsze się udaje. Potrzebujesz: mąki, cukru, jajek, masła i czekolady. Wszystko mieszamy i pieczemy przez 30 minut w 180 stopniach.',
        'category': cooking,
        'status': 'published',
        'published': timezone.now()
    }
)
if created:
    post4.tags.add(tag_recipe, tag_dessert)
    print(f"Created post: {post4.title}")

post5, created = Post.objects.get_or_create(
    slug='podroz-do-paryza',
    defaults={
        'title': 'Moja podróż do Paryża',
        'author': testuser,
        'body': 'Paryż to magiczne miasto pełne historii i kultury. W tym poście opowiem o mojej podróży do stolicy Francji. Zwiedziłem Wieżę Eiffla, Luwr i spacerowałem po Sekwanie. To była niezapomniana przygoda!',
        'category': travel,
        'status': 'published',
        'published': timezone.now()
    }
)
if created:
    post5.tags.add(tag_vacation, tag_europe)
    print(f"Created post: {post5.title}")

post6, created = Post.objects.get_or_create(
    slug='recenzja-ksiazki',
    defaults={
        'title': 'Recenzja: "Hobbit" J.R.R. Tolkien',
        'author': admin,
        'body': 'Dziś chciałbym podzielić się recenzją klasycznej powieści fantasy. "Hobbit" to wspaniała opowieść o przygodzie, przyjaźni i odwadze. Tolkien stworzył fascynujący świat, który do dziś zachwyca czytelników na całym świecie.',
        'category': culture,
        'status': 'published',
        'published': timezone.now()
    }
)
if created:
    post6.tags.add(tag_book)
    print(f"Created post: {post6.title}")

# Create draft post for testuser
draft_post, created = Post.objects.get_or_create(
    slug='moj-szkic',
    defaults={
        'title': 'Mój szkic posta',
        'author': testuser,
        'body': 'To jest post w statusie draft. Zostanie opublikowany po akceptacji przez administratora. W tym poście chciałbym podzielić się moimi przemyśleniami na temat...',
        'category': life,
        'status': 'draft',
        'published': timezone.now()
    }
)
if created:
    draft_post.tags.add(tag_health)
    print(f"Created draft post: {draft_post.title}")

# Create comments for testuser
# 2 approved comments
comment1, created = Comment.objects.get_or_create(
    post=obj,
    user=testuser,
    defaults={
        'name': testuser.get_full_name() or testuser.username,
        'email': testuser.email or 'testuser@example.com',
        'body': 'Świetny post! Dzięki za udostępnienie tych informacji.',
        'approved': True
    }
)
if created:
    print(f"Created approved comment on post: {obj.title}")

comment2, created = Comment.objects.get_or_create(
    post=post2,
    user=testuser,
    defaults={
        'name': testuser.get_full_name() or testuser.username,
        'email': testuser.email or 'testuser@example.com',
        'body': 'Bardzo pomocny tutorial. Czekam na więcej takich wpisów!',
        'approved': True
    }
)
if created:
    print(f"Created approved comment on post: {post2.title}")

# 2 unapproved comments
comment3, created = Comment.objects.get_or_create(
    post=post3,
    user=testuser,
    defaults={
        'name': testuser.get_full_name() or testuser.username,
        'email': testuser.email or 'testuser@example.com',
        'body': 'Mam pytanie dotyczące diety. Czy mogę zadać pytanie?',
        'approved': False
    }
)
if created:
    print(f"Created unapproved comment on post: {post3.title}")

comment4, created = Comment.objects.get_or_create(
    post=post4,
    user=testuser,
    defaults={
        'name': testuser.get_full_name() or testuser.username,
        'email': testuser.email or 'testuser@example.com',
        'body': 'Wygląda pysznie! Muszę spróbować tego przepisu.',
        'approved': False
    }
)
if created:
    print(f"Created unapproved comment on post: {post4.title}")

print("\n" + "="*50)
print("Seed data created successfully!")
print("="*50)
print(f"Categories: {Category.objects.count()}")
print(f"Tags: {Tag.objects.count()}")
print(f"Users: {User.objects.count()}")
print(f"Published posts: {Post.objects.filter(status='published').count()}")
print(f"Draft posts: {Post.objects.filter(status='draft').count()}")
print(f"Approved comments: {Comment.objects.filter(approved=True).count()}")
print(f"Unapproved comments: {Comment.objects.filter(approved=False).count()}")
print("="*50)
