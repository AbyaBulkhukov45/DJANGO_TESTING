from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()

HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')

DETAIL_URL = reverse('notes:detail', args=['Slugg'])
EDIT_URL = reverse('notes:edit', args=['Slugg'])
DELETE_URL = reverse('notes:delete', args=['Slugg'])


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.client = Client()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Slugg',
            author=cls.author
        )

    def test_all_route_access(self):
        route_cases = [
            (self.author, HOME_URL, HTTPStatus.OK),
            (self.reader, HOME_URL, HTTPStatus.OK),
            (self.author, LOGIN_URL, HTTPStatus.OK),
            (self.reader, LOGIN_URL, HTTPStatus.OK),
            (self.author, LOGOUT_URL, HTTPStatus.OK),
            (self.reader, LOGOUT_URL, HTTPStatus.OK),
            (self.author, SIGNUP_URL, HTTPStatus.OK),
            (self.reader, SIGNUP_URL, HTTPStatus.OK),
            (self.author, ADD_URL, HTTPStatus.OK),
            (self.author, SUCCESS_URL, HTTPStatus.OK),
            (self.author, DETAIL_URL, HTTPStatus.OK),
            (self.reader, DETAIL_URL, HTTPStatus.NOT_FOUND),
            (self.author, EDIT_URL, HTTPStatus.OK),
            (self.reader, EDIT_URL, HTTPStatus.NOT_FOUND),
            (self.author, DELETE_URL, HTTPStatus.OK),
            (self.reader, DELETE_URL, HTTPStatus.NOT_FOUND),
        ]

        for user, url, expected_status in route_cases:
            with self.subTest(user=user, url=url):
                self.client.force_login(user)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
