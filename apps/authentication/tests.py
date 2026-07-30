from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

User = get_user_model()

class IsolatedSessionMiddlewareTest(TestCase):
    def setUp(self):
        # Create regular user (non-staff)
        self.user = User.objects.create_user(
            username='regularuser',
            email='regularuser@example.com',
            password='Password123!',
            first_name='Regular',
            last_name='User'
        )
        # Create staff user for admin
        self.staff_user = User.objects.create_superuser(
            username='adminuser',
            email='adminuser@example.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User'
        )
        self.client = Client()

    def test_application_login_success_and_session_persistence(self):
        """Test regular user login, session cookie creation, and access to protected dashboard."""
        response = self.client.post(reverse('login'), {
            'username': 'regularuser',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard:home'))
        
        # Verify app session cookie exists
        session_cookie = self.client.cookies.get(settings.SESSION_COOKIE_NAME)
        self.assertIsNotNone(session_cookie)
        self.assertTrue(len(session_cookie.value) > 0)

        # Verify access to protected dashboard page
        dashboard_response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(dashboard_response.status_code, 200)

    def test_anonymous_access_redirects_to_login(self):
        """Test unauthenticated request to dashboard redirects to login page."""
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_staff_user_blocked_from_frontend_login(self):
        """Test staff/superuser is restricted from logging into the frontend app."""
        response = self.client.post(reverse('login'), {
            'username': 'adminuser',
            'password': 'AdminPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This account is restricted to the Admin Panel.")


    def test_application_logout(self):
        """Test application logout clears session and redirects to login."""
        self.client.login(username='regularuser', password='Password123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Verify dashboard is no longer accessible
        dashboard_response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(dashboard_response.status_code, 302)

    def test_admin_session_cookie_isolation(self):
        """Test that Admin login creates admin_sessionid cookie, keeping app session isolated."""
        admin_client = Client()
        response = admin_client.post('/admin/login/', {
            'username': 'adminuser',
            'password': 'AdminPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify admin_sessionid cookie was set
        admin_cookie = admin_client.cookies.get('admin_sessionid')
        self.assertIsNotNone(admin_cookie)
        self.assertTrue(len(admin_cookie.value) > 0)

    def test_csrf_token_session_isolation(self):
        """Test that logging into Admin does not invalidate Application CSRF tokens when CSRF_USE_SESSIONS=True."""
        client = Client(enforce_csrf_checks=True)
        import re

        # 1. GET App login page
        res_app_get = client.get(reverse('login'))
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', res_app_get.content.decode('utf-8'))
        app_csrf_token = match.group(1)

        # 2. Interleave Admin login in the same browser session
        res_admin_get = client.get('/admin/login/')
        admin_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', res_admin_get.content.decode('utf-8'))
        admin_csrf_token = admin_match.group(1)

        res_admin_login = client.post('/admin/login/', {
            'csrfmiddlewaretoken': admin_csrf_token,
            'username': 'adminuser',
            'password': 'AdminPassword123!'
        })
        self.assertEqual(res_admin_login.status_code, 302)

        # 3. Post to App login using original App token
        res_app_post = client.post(reverse('login'), {
            'csrfmiddlewaretoken': app_csrf_token,
            'username': 'regularuser',
            'password': 'Password123!'
        })
        self.assertEqual(res_app_post.status_code, 302)


