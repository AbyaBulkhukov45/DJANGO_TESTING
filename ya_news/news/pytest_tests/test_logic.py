import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from http import HTTPStatus
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, text_comment):
    url = reverse('news:detail', args=(news.id,))
    client = Client()
    client.post(url, data=text_comment)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(news, author_client, text_comment):
    url = reverse('news:detail', args=(news.id,))
    client = author_client
    response = client.post(url, data=text_comment)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == text_comment['text']
    assert comment.news == news


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    client = author_client
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    form = response.context['form']
    assert form.errors['text'] == [WARNING]
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    client = author_client
    url = reverse('news:delete', args=(comment.id,))
    response = client.delete(url)
    assert response.status_code == HTTPStatus.FOUND
    x = f'{reverse("news:detail",args=(comment.news.id,))}#comments'
    # x - потому что не проходило pep8 так бы не делал)
    assert response.url == x
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(client_data, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = client_data.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


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


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(client_data,
                                                comment,
                                                edit_comment_data):
    url = reverse('news:edit', args=(comment.id,))
    response = client_data.post(url, data=edit_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != edit_comment_data['text']
