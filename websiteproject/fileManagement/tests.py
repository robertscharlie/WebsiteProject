from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import UploadedFile


class FileUploadValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pw')
        self.client.force_login(self.user)

    def test_rejects_disallowed_extension(self):
        f = SimpleUploadedFile('virus.exe', b'x')
        response = self.client.post('/files/upload/', {'title': 'Bad', 'file': f})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors.get('file'))
        self.assertEqual(UploadedFile.objects.count(), 0)

    @override_settings(MAX_UPLOAD_SIZE_MB=1)
    def test_rejects_file_over_size_limit(self):
        f = SimpleUploadedFile('big.txt', b'x' * (2 * 1024 * 1024))
        response = self.client.post('/files/upload/', {'title': 'Big', 'file': f})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UploadedFile.objects.count(), 0)

    def test_accepts_allowed_file(self):
        f = SimpleUploadedFile('notes.txt', b'hello')
        response = self.client.post('/files/upload/', {'title': 'Notes', 'file': f})
        self.assertRedirects(response, '/files/upload/')
        self.assertEqual(UploadedFile.objects.count(), 1)


class FileSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pw')
        self.client.force_login(self.user)
        UploadedFile.objects.create(
            user=self.user, title='Holiday photo', file=SimpleUploadedFile('a.txt', b'x')
        )
        UploadedFile.objects.create(
            user=self.user, title='Work report', file=SimpleUploadedFile('b.txt', b'x')
        )

    def test_search_filters_by_title(self):
        response = self.client.get('/files/', {'q': 'holiday'})
        titles = [f.title for f in response.context['files']]
        self.assertEqual(titles, ['Holiday photo'])

    def test_empty_search_shows_all(self):
        response = self.client.get('/files/')
        self.assertEqual(len(response.context['files']), 2)


class FileRenameDeleteTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='alice', password='pw')
        self.other = User.objects.create_user(username='bob', password='pw')
        self.upload = UploadedFile.objects.create(
            user=self.owner, title='Original', file=SimpleUploadedFile('a.txt', b'x')
        )

    def test_owner_can_rename(self):
        self.client.force_login(self.owner)
        response = self.client.post(f'/files/edit/{self.upload.pk}/', {'title': 'Renamed'})
        self.assertRedirects(response, '/files/')
        self.upload.refresh_from_db()
        self.assertEqual(self.upload.title, 'Renamed')

    def test_owner_can_delete(self):
        self.client.force_login(self.owner)
        response = self.client.post(f'/files/delete/{self.upload.pk}/')
        self.assertRedirects(response, '/files/')
        self.assertEqual(UploadedFile.objects.count(), 0)

    def test_delete_requires_post(self):
        self.client.force_login(self.owner)
        response = self.client.get(f'/files/delete/{self.upload.pk}/')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(UploadedFile.objects.count(), 1)

    def test_other_user_cannot_rename(self):
        self.client.force_login(self.other)
        response = self.client.post(f'/files/edit/{self.upload.pk}/', {'title': 'Hijacked'})
        self.assertEqual(response.status_code, 404)
        self.upload.refresh_from_db()
        self.assertEqual(self.upload.title, 'Original')

    def test_other_user_cannot_delete(self):
        self.client.force_login(self.other)
        response = self.client.post(f'/files/delete/{self.upload.pk}/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(UploadedFile.objects.count(), 1)
