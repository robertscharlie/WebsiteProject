from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RandomPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pw')

    def test_redirects_anonymous_users_to_login(self):
        response = self.client.get(reverse('random:random'))
        self.assertRedirects(response, f"/login/?next={reverse('random:random')}")

    def test_loads_for_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('random:random'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'randomTools/random.html')
