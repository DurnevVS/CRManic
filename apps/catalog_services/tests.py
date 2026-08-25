from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import Master
from apps.clients.models import Client

from .models import CompletedService, Service


def create_master(phone: str) -> Master:
    master = Master(phone=phone)
    master.set_unusable_password()
    master.save()
    return master


class ServiceValidationTests(TestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")

    def test_price_cannot_be_negative(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Service.objects.create(
                master=self.master,
                name="Маникюр",
                price=Decimal("-1.00"),
            )

    def test_material_cost_cannot_be_negative(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Service.objects.create(
                master=self.master,
                name="Маникюр",
                price=Decimal("1000.00"),
                estimated_material_cost=Decimal("-1.00"),
            )

    def test_zero_price_and_material_cost_are_allowed(self):
        service = Service(
            master=self.master,
            name="Бесплатная услуга",
            price=Decimal("0.00"),
            estimated_material_cost=Decimal("0.00"),
        )

        service.full_clean()


class CompletedServiceValidationTests(TestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")
        self.client = Client.objects.create(
            master=self.master,
            name="Клиент",
            phone="+79991234568",
        )
        self.service = Service.objects.create(
            master=self.master,
            name="Маникюр",
            price=Decimal("1000.00"),
        )

    def test_client_must_belong_to_master(self):
        another_master = create_master(phone="+79991234569")
        another_client = Client.objects.create(
            master=another_master,
            name="Другой клиент",
            phone="+79991234570",
        )
        completed_service = CompletedService(
            master=self.master,
            client=another_client,
            service=self.service,
            service_name=self.service.name,
            price=self.service.price,
        )

        with self.assertRaises(ValidationError):
            completed_service.full_clean()

    def test_service_must_belong_to_master(self):
        another_master = create_master(phone="+79991234569")
        another_service = Service.objects.create(
            master=another_master,
            name="Педикюр",
            price=Decimal("1500.00"),
        )
        completed_service = CompletedService(
            master=self.master,
            client=self.client,
            service=another_service,
            service_name=another_service.name,
            price=another_service.price,
        )

        with self.assertRaises(ValidationError):
            completed_service.full_clean()

    def test_price_cannot_be_negative(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            CompletedService.objects.create(
                master=self.master,
                client=self.client,
                service=self.service,
                service_name=self.service.name,
                price=Decimal("-1.00"),
            )

    def test_valid_completed_service_passes_validation(self):
        completed_service = CompletedService(
            master=self.master,
            client=self.client,
            service=self.service,
            service_name=self.service.name,
            price=self.service.price,
        )

        completed_service.full_clean()
        completed_service.save()

        self.assertEqual(completed_service.client, self.client)
