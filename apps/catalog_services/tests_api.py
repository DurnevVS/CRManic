from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.accounts.models import Master
from apps.clients.models import Client

from .models import CompletedService, Service


def create_master(phone: str) -> Master:
    master = Master(phone=phone)
    master.set_unusable_password()
    master.save()
    return master


class CatalogServicesAPITests(APITestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")
        self.another_master = create_master(phone="+79991234568")
        self.client_model = Client.objects.create(
            master=self.master,
            name="Клиент",
            phone="+79991234569",
        )
        self.service = Service.objects.create(
            master=self.master,
            name="Маникюр",
            price=Decimal("1000.00"),
        )
        token = Token.objects.create(user=self.master)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_service_is_created_for_current_master(self):
        response = self.client.post(
            reverse("service-list"),
            {"name": "Педикюр", "price": "1500.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Service.objects.filter(
                pk=response.data["id"],
                master=self.master,
            ).exists()
        )

    def test_negative_service_price_is_rejected(self):
        response = self.client.post(
            reverse("service-list"),
            {"name": "Педикюр", "price": "-1.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_completed_service_is_created_for_current_master(self):
        response = self.client.post(
            reverse("completed-service-list"),
            {
                "client": self.client_model.pk,
                "service": self.service.pk,
                "service_name": self.service.name,
                "price": "1000.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CompletedService.objects.filter(
                pk=response.data["id"],
                master=self.master,
            ).exists()
        )

    def test_client_of_another_master_cannot_be_used(self):
        another_client = Client.objects.create(
            master=self.another_master,
            name="Чужой клиент",
            phone="+79991234570",
        )

        response = self.client.post(
            reverse("completed-service-list"),
            {
                "client": another_client.pk,
                "service": self.service.pk,
                "service_name": self.service.name,
                "price": "1000.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("client", response.data)
