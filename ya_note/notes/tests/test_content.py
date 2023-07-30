from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
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

    def test_pages_contain_form(self):
        page_names = ['notes:add', 'notes:edit']
        self.client.force_login(self.author)
        for name in page_names:
            with self.subTest(name=name):
                if name == 'notes:add':
                    url = reverse(name)
                else:
                    url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertIn('form', response.context)

    def test_notes_list_for_author_and_reader_client(self):
        Users_statuses = (self.author, self.reader)
        for user_stat in Users_statuses:
            with self.subTest(user_stat=user_stat):
                self.client.force_login(user_stat)
                url = reverse('notes:list')
                response = self.client.get(url)
                object_list = response.context['object_list']
                if user_stat == self.author:
                    self.assertIn(self.note, object_list)
                else:
                    self.assertNotIn(self.note, object_list)

    def test_note_to_list(self):
        self.client.force_login(self.author)
        new_note = Note.objects.create(
            title='Новая зам',
            text='нов зам',
            slug='Newnote',
            author=self.author
        )
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertTrue(any(note.text == 'нов зам' for note in object_list))
        self.assertEqual(Note.objects.count(), 2)
        self.assertIn(new_note, object_list)
