from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import UserProfile, Item

@override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='student', email='student@sdu.edu.kz', password='Good-password-123')
        UserProfile.objects.create(user=self.user)

    def test_email_login_session_and_logout(self):
        response = self.client.post(reverse('login'), {'username': self.user.email, 'password': 'Good-password-123'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertTrue(self.client.get(reverse('account')).context['user'].is_authenticated)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_invalid_or_inactive_login_fails_generically(self):
        for email, password in [('student@sdu.edu.kz', 'wrong'), ('missing@sdu.edu.kz', 'wrong')]:
            response = self.client.post(reverse('login'), {'username': email, 'password': password})
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('_auth_user_id', self.client.session)
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse('login'), {'username': self.user.email, 'password': 'Good-password-123'})
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_protected_api_owner_and_role(self):
        self.assertEqual(self.client.post('/api/items/', {'title': 'x', 'contact': 'x'}).status_code, 401)
        self.client.force_login(self.user)
        created = self.client.post('/api/items/', {'title': 'x', 'contact': 'x'})
        item_id = created.json()['item']['id']
        self.assertEqual(self.client.delete(f'/api/items/{item_id}/').status_code, 200)

    def test_csrf_required_for_login(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse('login'), {'username': self.user.email, 'password': 'Good-password-123'})
        self.assertEqual(response.status_code, 403)
