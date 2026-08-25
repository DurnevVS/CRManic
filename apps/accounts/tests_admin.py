from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from apps.catalog_services.models import CompletedService, Service
from apps.clients.models import Client
from apps.expenses.models import Expense, ExpenseGroup, ExpenseTemplate
from apps.schedule.models import AppointmentSlot, ScheduleDay

from .admin import MasterAdmin
from .models import Master


class AdminRegistrationTests(TestCase):
    def setUp(self):
        self.superuser = Master(
            phone="+79991234567",
            is_staff=True,
            is_superuser=True,
        )
        self.superuser.set_password("StrongPass123")
        self.superuser.save()
        self.client.force_login(self.superuser)

    def test_all_business_models_are_registered(self):
        business_models = (
            Master,
            Client,
            Service,
            CompletedService,
            ScheduleDay,
            AppointmentSlot,
            ExpenseGroup,
            Expense,
            ExpenseTemplate,
        )

        for model in business_models:
            with self.subTest(model=model.__name__):
                self.assertIn(model, admin.site._registry)

    def test_master_uses_custom_user_admin(self):
        self.assertEqual(admin.site._registry[Master].__class__, MasterAdmin)

    def test_all_business_model_lists_are_available(self):
        model_names = (
            "accounts_master",
            "clients_client",
            "catalog_services_service",
            "catalog_services_completedservice",
            "schedule_scheduleday",
            "schedule_appointmentslot",
            "expenses_expensegroup",
            "expenses_expense",
            "expenses_expensetemplate",
        )

        for model_name in model_names:
            with self.subTest(model_name=model_name):
                response = self.client.get(
                    reverse(f"admin:{model_name}_changelist")
                )
                self.assertEqual(response.status_code, 200)

    def test_master_can_be_created_in_admin(self):
        response = self.client.post(
            reverse("admin:accounts_master_add"),
            {
                "phone": "+79991234568",
                "password1": "AnotherStrongPass123",
                "password2": "AnotherStrongPass123",
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Master.objects.filter(phone="+79991234568").exists())
