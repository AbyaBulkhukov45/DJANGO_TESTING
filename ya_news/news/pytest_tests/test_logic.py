import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, text_comment, urls):
    client = Client()
    comments_count_before = Comment.objects.count()

    response = client.post(urls['detail'], data=text_comment)

    comments_count_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.FOUND
    assert comments_count_before == comments_count_after


@pytest.mark.django_db
def test_user_create_comment(news, author_client, text_comment, author, urls):
    url = urls['detail']
    client = author_client
    response = client.post(url, data=text_comment)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == text_comment['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news, urls):
    client = author_client
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count_before = Comment.objects.count()
    response = client.post(urls['detail'], data=bad_words_data)
    comments_count_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    form = response.context['form']
    assert form.errors['text'] == [WARNING]
    assert comments_count_before == comments_count_after


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    client = author_client
    url = reverse('news:delete', args=(comment.id,))
    comments_count_before = Comment.objects.count()
    response = client.delete(url)
    comments_count_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.FOUND
    comment_url = f'{reverse("news:detail", args=(comment.news.id,))}#comments'
    assert response.url == comment_url
    assert comments_count_after == comments_count_before - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(client_data, comment):
    url = reverse('news:delete', args=(comment.id,))
    comments_count_before = Comment.objects.count()
    response = client_data.delete(url)
    comments_count_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count_after == comments_count_before


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, edit_comment_data):
    client = author_client
    url = reverse('news:edit', args=(comment.id,))
    response = client.post(url, data=edit_comment_data)
    assert response.status_code == HTTPStatus.FOUND
    x = f'{reverse("news:detail", args=(comment.news.id,))}#comments'
    assert response.url == x
    comment.refresh_from_db()
    assert comment.text == edit_comment_data['text']
    assert comment.news == comment.news
    assert comment.author == comment.author
    assert comment.created == comment.created


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(client_data,
                                                comment,
                                                edit_comment_data):
    url = reverse('news:edit', args=(comment.id,))

    initial_text = comment.text
    initial_author = comment.author
    initial_news = comment.news

    response = client_data.post(url, data=edit_comment_data)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text == initial_text
    assert comment.author == initial_author
    assert comment.news == initial_news
