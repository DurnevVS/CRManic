from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Master


def create_master(phone: str, password: str = "StrongPass123") -> Master:
    master = Master(phone=phone)
    master.set_password(password)
    master.save()
    return master


class AuthenticationAPITests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123"
        self.master = create_master(
            phone="+79991234567",
            password=self.password,
        )

    def authenticate(self):
        token = Token.objects.create(user=self.master)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_token_can_be_obtained_with_phone_and_password(self):
        response = self.client.post(
            reverse("auth-token"),
            {"phone": self.master.phone, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_invalid_credentials_are_rejected(self):
        response = self.client.post(
            reverse("auth-token"),
            {"phone": self.master.phone, "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_requires_authentication(self):
        response = self.client.get(reverse("client-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_master_can_read_and_update_profile(self):
        self.authenticate()

        response = self.client.patch(
            reverse("me"),
            {"first_name": "Анна"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.master.refresh_from_db()
        self.assertEqual(self.master.first_name, "Анна")

    def test_logout_revokes_token(self):
        self.authenticate()

        response = self.client.post(reverse("auth-logout"), format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.master).exists())
        self.assertEqual(
            self.client.get(reverse("me")).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_openapi_schema_and_documentation_are_public(self):
        schema_response = self.client.get(reverse("api-schema"))
        docs_response = self.client.get(reverse("api-docs"))

        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)
        self.assertEqual(docs_response.status_code, status.HTTP_200_OK)
