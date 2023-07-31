import pytest
from http import HTTPStatus

from django.urls import reverse
from django.test import Client
from pytest_django.asserts import assertRedirects


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, client, expected_status_code',
    [
        (reverse('news:home'), Client(), HTTPStatus.OK),
        (reverse('news:detail', args=[1]), Client(), HTTPStatus.OK),
        (reverse('users:login'), Client(), HTTPStatus.OK),
        (reverse('users:logout'), Client(), HTTPStatus.OK),
        (reverse('users:signup'), Client(), HTTPStatus.OK),
        (reverse('news:edit', args=[1]), Client(), HTTPStatus.FOUND),
        (reverse('news:delete', args=[1]), Client(), HTTPStatus.FOUND),
    ]
)
def test_status_codes_for_anon_user(news, client, url, expected_status_code):
    response = client.get(url)
    assert response.status_code == expected_status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, client, exp_status_code',
    [
        (reverse('news:edit', args=[1]), Client(), HTTPStatus.NOT_FOUND),
        (reverse('news:delete', args=[1]), Client(), HTTPStatus.NOT_FOUND),
    ]
)
def test_stat_code_admin(news, client, url, exp_status_code, admin_client):
    client = admin_client
    response = client.get(url)
    assert response.status_code == exp_status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirects_for_anonymous_user(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=[comment.id])
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
