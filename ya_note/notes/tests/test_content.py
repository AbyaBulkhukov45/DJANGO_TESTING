from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()

NOTES_ADD_URL = reverse('notes:add')
NOTES_EDIT_URL = reverse('notes:edit', args=['Slugg'])
NOTES_LIST_URL = reverse('notes:list')


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Slugg',
            author=cls.author
        )
        cls.client = Client()

    def setUp(self):
        self.client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def test_pages_contain_form(self):
        page_names = [NOTES_ADD_URL, NOTES_EDIT_URL]
        for url in page_names:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)

    def test_notes_list_for_author_and_reader_client(self):
        Users_statuses = (self.author, self.reader)
        for user_stat in Users_statuses:
            with self.subTest(user_stat=user_stat):
                self.client.force_login(user_stat)
                response = self.client.get(NOTES_LIST_URL)
                object_list = response.context['object_list']
                if user_stat == self.author:
                    self.assertIn(self.note, object_list)
                else:
                    self.assertNotIn(self.note, object_list)

    def test_note_to_list(self):
        new_note = Note.objects.create(
            title='Новая заметка',
            text='новая заметка',
            slug='Newnote',
            author=self.author
        )
        response = self.author_client.get(NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertTrue(
            any(note.text == 'новая заметка' for note in object_list))
        self.assertEqual(Note.objects.count(), 2)
        self.assertIn(new_note, object_list)
