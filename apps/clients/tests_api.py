from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.accounts.models import Master

from .models import Client


def create_master(phone: str) -> Master:
    master = Master(phone=phone)
    master.set_unusable_password()
    master.save()
    return master


class ClientAPITests(APITestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")
        self.another_master = create_master(phone="+79991234568")
        token = Token.objects.create(user=self.master)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_list_contains_only_current_master_clients(self):
        own_client = Client.objects.create(
            master=self.master,
            name="Свой клиент",
            phone="+79991234569",
        )
        Client.objects.create(
            master=self.another_master,
            name="Чужой клиент",
            phone="+79991234570",
        )

        response = self.client.get(reverse("client-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], own_client.pk)

    def test_client_crud(self):
        create_response = self.client.post(
            reverse("client-list"),
            {"name": "Клиент", "phone": "+79991234569"},
            format="json",
        )
        client_id = create_response.data["id"]

        update_response = self.client.patch(
            reverse("client-detail", args=(client_id,)),
            {"comment": "Постоянный клиент"},
            format="json",
        )
        delete_response = self.client.delete(
            reverse("client-detail", args=(client_id,))
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Client.objects.filter(pk=client_id).exists())

    def test_client_of_another_master_returns_not_found(self):
        another_client = Client.objects.create(
            master=self.another_master,
            name="Чужой клиент",
            phone="+79991234569",
        )

        response = self.client.get(
            reverse("client-detail", args=(another_client.pk,))
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_future_birthday_is_rejected(self):
        response = self.client.post(
            reverse("client-list"),
            {
                "name": "Клиент",
                "phone": "+79991234569",
                "birthday": date.today() + timedelta(days=1),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("birthday", response.data)
