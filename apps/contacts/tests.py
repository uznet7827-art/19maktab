from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from .models import Contact


class ContactTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_contact_get_view(self):
        response = self.client.get(reverse('contacts:contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_submission_success(self):
        data = {
            'full_name': 'Ali Valiyev',
            'phone': '+998901234567',
            'email': 'ali@example.com',
            'contact_type': 'general',
            'subject': 'Savol maktab haqida',
            'message': 'Maktab qabul jarayoni qachon boshlanadi?',
            'privacy_agreed': True,
        }
        response = self.client.post(reverse('contacts:contact'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Contact.objects.filter(full_name='Ali Valiyev').exists())

    def test_contact_submission_missing_privacy(self):
        data = {
            'full_name': 'Vali Aliyev',
            'phone': '+998901234567',
            'email': 'vali@example.com',
            'contact_type': 'general',
            'subject': 'Test mavzu',
            'message': 'Test xabar',
            'privacy_agreed': False,
        }
        response = self.client.post(reverse('contacts:contact'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contact.objects.filter(full_name='Vali Aliyev').exists())

    def test_contact_rate_limiting(self):
        data = {
            'full_name': 'Test User',
            'phone': '+998901234567',
            'email': 'test@example.com',
            'contact_type': 'general',
            'subject': 'Test Mavzu',
            'message': 'Test xabar matni',
            'privacy_agreed': True,
        }
        # First 3 submissions should succeed (redirects with 302 -> 200 follow)
        for i in range(3):
            res = self.client.post(reverse('contacts:contact'), data, REMOTE_ADDR='192.168.1.100')
            self.assertEqual(res.status_code, 302)

        # 4th submission should be rate limited with HTTP 429
        res4 = self.client.post(reverse('contacts:contact'), data, REMOTE_ADDR='192.168.1.100')
        self.assertEqual(res4.status_code, 429)
