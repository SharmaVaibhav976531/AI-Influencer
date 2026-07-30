from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class SidebarNavigationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='nav_user',
            email='nav@example.com',
            password='Password123!'
        )
        self.client = Client()
        self.client.login(username='nav_user', password='Password123!')

    def test_dashboard_home_navigation(self):
        url = reverse('dashboard:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="' + reverse('dashboard:home') + '"')
        self.assertNotContains(response, 'href="#"')

    def test_uploads_navigation(self):
        url = reverse('uploads:upload')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="' + reverse('uploads:upload') + '"')

    def test_upload_history_navigation(self):
        url = reverse('uploads:history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="' + reverse('uploads:history') + '"')

    def test_influencers_discovery_navigation(self):
        url = reverse('influencers:discovery')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="' + reverse('influencers:discovery') + '"')

    def test_nlp_dashboard_navigation(self):
        url = reverse('influencers:nlp_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="' + reverse('influencers:nlp_dashboard') + '"')

    def test_ai_classification_navigation(self):
        url = reverse('influencers:ai_classification')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="' + reverse('influencers:ai_classification') + '"')

    def test_results_list_navigation(self):
        url = reverse('influencers:results_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="' + reverse('influencers:results_list') + '"')

    def test_analytics_navigation(self):
        url = reverse('dashboard:analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="' + reverse('dashboard:analytics') + '"')

    def test_no_placeholder_hash_urls_in_sidebar(self):
        """Verify sidebar contains zero href='#' placeholder links."""
        url = reverse('dashboard:home')
        response = self.client.get(url)
        content = response.content.decode('utf-8')
        self.assertNotIn('href="#"', content)
