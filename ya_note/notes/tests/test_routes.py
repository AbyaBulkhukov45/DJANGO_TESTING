from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from notes.models import Note
from http import HTTPStatus

User = get_user_model()


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

    def test_availability_home_and_login_for_all_users(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:home',
                         'users:login',
                         'users:logout',
                         'users:signup'):
                with self.subTest(user=user, name=name):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_notes_add_done_for_author(self):
        users_statuses = (
            (self.author, 200),
        )
        page_names = ['notes:home', 'notes:add', 'notes:success']
        for user, status in users_statuses:
            with self.subTest(user=user):
                self.client.force_login(user)
                for name in page_names:
                    with self.subTest(name=name):
                        url = reverse(name)
                        response = self.client.get(url)
                        self.assertEqual(response.status_code, status)

    def test_availability_notes_add_done_for_all_users(self):
        users_statuses = (
            (self.author, 200),
            (self.reader, 404)
        )
        page_names = ['notes:detail', 'notes:edit', 'notes:delete']
        for user, status in users_statuses:
            with self.subTest(user=user):
                self.client.force_login(user)
                for name in page_names:
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
