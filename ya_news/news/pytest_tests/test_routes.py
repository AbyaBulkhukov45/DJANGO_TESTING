import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', "1"),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_different_pages_for_anonymous_user(client, name, news, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


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


@pytest.mark.django_db
@pytest.mark.parametrize('view_name', ['edit', 'delete'])
def test_access_to_comment_pages(author_client, client, comment, view_name):
    url = reverse(f'news:{view_name}', args=[comment.id])
    expected_redirect_url = reverse('users:login')

    if author_client:
        response = author_client.get(url)
        assert response.status_code == HTTPStatus.OK
    else:
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url.startswith(expected_redirect_url)
