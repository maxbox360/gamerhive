from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class SessionAuthenticationConfigurationTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = get_user_model().objects.create_user(
            username="session-user",
            email="session-user@example.com",
            password="S3curePass123!",
        )

    def test_csrf_bootstrap_sets_cookie(self):
        response = self.client.get("/api/auth/csrf")

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrfToken", response.json())
        self.assertIn("csrftoken", response.cookies)

    def test_session_authentication_makes_user_available(self):
        self.client.force_login(self.user)

        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user, self.user)
