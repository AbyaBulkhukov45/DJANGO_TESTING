from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify


User = get_user_model()

URL_NOTES_ADD = reverse('notes:add')
URL_NOTES_SUCCESS = reverse('notes:success')
URL_USERS_LOGIN = reverse('users:login')


class TestLogic(TestCase):
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
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
        }
        cls.form_data['slug'] = slugify(cls.form_data['title'])

    def setUp(self):
        self.client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def test_user_can_create_note(self):
        response = self.author_client.post(URL_NOTES_ADD, data=self.form_data)
        self.assertRedirects(response, URL_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        initial_note_count = Note.objects.count()
        response = self.client.post(URL_NOTES_ADD, data=self.form_data)
        expected_url = f'{URL_USERS_LOGIN}?next={URL_NOTES_ADD}'
        final_note_count = Note.objects.count()
        self.assertEqual(final_note_count, initial_note_count)
        self.assertRedirects(response, expected_url)

    def test_not_unique_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        response = self.client.post(url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.author_client.post(URL_NOTES_ADD, data=self.form_data)
        self.assertRedirects(response, URL_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(title=self.form_data['title'])
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, URL_NOTES_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.reader_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        initial_note_count = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, URL_NOTES_SUCCESS)
        final_note_count = Note.objects.count()
        self.assertEqual(final_note_count, initial_note_count - 1)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
