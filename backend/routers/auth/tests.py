import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class RegistrationEndpointTests(TestCase):
    def setUp(self):
        self.payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass123!",
            "first_name": "New",
            "last_name": "User",
        }

    def test_successful_registration_creates_user_and_logs_in(self):
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(self.payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["username"], self.payload["username"])
        self.assertEqual(data["email"], self.payload["email"])
        self.assertEqual(data["first_name"], self.payload["first_name"])
        self.assertEqual(data["last_name"], self.payload["last_name"])
        self.assertNotIn("password", data)
        self.assertNotIn("password_hash", data)

        user = User.objects.get(username=self.payload["username"])
        self.assertTrue(user.check_password(self.payload["password"]))
        self.assertNotEqual(user.password, self.payload["password"])
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_missing_required_fields_are_validated(self):
        for field in ("username", "email", "password"):
            payload = dict(self.payload)
            payload.pop(field)
            response = self.client.post(
                "/api/auth/register",
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertIn(response.status_code, (400, 422))
            self.assertIn("detail", response.json())

    def test_invalid_password_is_rejected(self):
        payload = dict(self.payload)
        payload["password"] = "123"

        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertIn(response.status_code, (400, 422))
        self.assertIn("detail", response.json())

    def test_duplicate_username_and_email_are_rejected(self):
        User.objects.create_user(
            username=self.payload["username"],
            email=self.payload["email"],
            password=self.payload["password"],
        )

        username_dup = dict(self.payload)
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(username_dup),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

        email_dup = dict(self.payload)
        email_dup["username"] = "anotheruser"
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(email_dup),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())


class LoginEndpointTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="existinguser",
            email="existinguser@example.com",
            password="StrongPass123!",
        )

    def test_successful_login_sets_session_and_returns_safe_user_data(self):
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps({
                "username": "existinguser",
                "password": "StrongPass123!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(data["email"], self.user.email)
        self.assertNotIn("password", data)
        self.assertNotIn("password_hash", data)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

        follow_up = self.client.get("/api/users/")
        self.assertEqual(follow_up.status_code, 200)
        self.assertEqual(follow_up.wsgi_request.user, self.user)

    def test_incorrect_password_is_rejected_without_sensitive_details(self):
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps({
                "username": "existinguser",
                "password": "WrongPassword123!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())
        self.assertNotIn("existinguser@example.com", response.text)
        self.assertNotIn("password", response.text.lower())

    def test_unknown_username_is_rejected_without_sensitive_details(self):
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps({
                "username": "missinguser",
                "password": "StrongPass123!",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())
        self.assertNotIn("missinguser@example.com", response.text)

    def test_missing_credentials_are_rejected(self):
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps({"username": "", "password": ""}),
            content_type="application/json",
        )

        self.assertIn(response.status_code, (400, 422))
        self.assertIn("detail", response.json())


class LogoutEndpointTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username="logoutuser",
            email="logoutuser@example.com",
            password="StrongPass123!",
        )

    def _logout(self):
        csrf_response = self.client.get("/api/auth/csrf")
        self.assertEqual(csrf_response.status_code, 200)
        csrf_token = csrf_response.json()["csrfToken"]

        return self.client.post(
            "/api/auth/logout",
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )


    def test_successful_logout_clears_authenticated_session(self):
        self.client.force_login(self.user)
        pre_logout = self.client.get("/api/users/")
        self.assertEqual(pre_logout.status_code, 200)
        self.assertEqual(pre_logout.wsgi_request.user, self.user)

        response = self._logout()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        self.assertNotIn("_auth_user_id", self.client.session)

        post_logout = self.client.get("/api/users/")
        self.assertEqual(post_logout.status_code, 200)
        self.assertFalse(post_logout.wsgi_request.user.is_authenticated)

    def test_unauthenticated_logout_returns_success(self):
        response = self._logout()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        self.assertNotIn("_auth_user_id", self.client.session)
