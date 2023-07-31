import pytest
from news.models import News, Comment
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='user')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        date=datetime(2023, 6, 1),
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text="Text of comment",
    )
    return comment


@pytest.fixture
def news_data():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    yield
    News.objects.all().delete()


@pytest.fixture
def comment_data():
    news = News.objects.create(title='Тестовая новость', text='Просто текст.')
    author = User.objects.create(username='Комментатор')
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    yield
    Comment.objects.all().delete()
    User.objects.all().delete()
    News.objects.all().delete()


@pytest.fixture
def text_comment():
    return {'text': 'Текст для коммента'}


@pytest.fixture
def edit_comment_data():
    return {'text': 'Обновлённый комментарий'}


@pytest.fixture
def client_data():
    user = User.objects.create(username='Анонимус')
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def urls(news):
    return {
        'home': reverse('news:home'),
        'detail': reverse('news:detail', args=[News.objects.first().id]),
    }


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create(username='user')


@pytest.fixture
def admin_client(admin, client):
    client.force_login(admin)
    return client
