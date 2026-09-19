from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from gamerhive.api import api


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

    def test_ninja_api_has_csrf_enabled(self):
        self.assertTrue(getattr(api, "csrf", False))

    def test_session_authentication_makes_user_available(self):
        self.client.force_login(self.user)

        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user, self.user)

    @override_settings(ROOT_URLCONF="routers.games.tests.csrf_test_urls")
    def test_unsafe_requests_require_csrf_token(self):
        self.client.force_login(self.user)

        response = self.client.post(
            "/api/csrf-probe",
            data="{}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    @override_settings(ROOT_URLCONF="routers.games.tests.csrf_test_urls")
    def test_unsafe_requests_accept_valid_csrf_token(self):
        self.client.force_login(self.user)
        csrf_response = self.client.get("/api/auth/csrf")

        response = self.client.post(
            "/api/csrf-probe",
            data="{}",
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_response.json()["csrfToken"],
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"authenticated": True})
