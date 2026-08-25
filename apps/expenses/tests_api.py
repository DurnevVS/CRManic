from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.accounts.models import Master
from apps.schedule.models import ScheduleDay

from .models import Expense, ExpenseGroup, ExpenseTemplate


def create_master(phone: str) -> Master:
    master = Master(phone=phone)
    master.set_unusable_password()
    master.save()
    return master


class ExpensesAPITests(APITestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")
        self.another_master = create_master(phone="+79991234568")
        self.schedule_day = ScheduleDay.objects.create(
            master=self.master,
            date=date(2026, 8, 25),
        )
        self.global_group = ExpenseGroup.objects.get(
            name="Расходники",
            master__isnull=True,
        )
        token = Token.objects.create(user=self.master)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_group_list_contains_global_and_own_groups(self):
        own_group = ExpenseGroup.objects.create(
            master=self.master,
            name="Обучение",
        )
        another_group = ExpenseGroup.objects.create(
            master=self.another_master,
            name="Реклама",
        )

        response = self.client.get(reverse("expense-group-list"))
        group_ids = {item["id"] for item in response.data["results"]}

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.global_group.pk, group_ids)
        self.assertIn(own_group.pk, group_ids)
        self.assertNotIn(another_group.pk, group_ids)

    def test_global_group_cannot_be_changed(self):
        response = self.client.patch(
            reverse("expense-group-detail", args=(self.global_group.pk,)),
            {"name": "Новое название"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_personal_group_is_created_for_current_master(self):
        response = self.client.post(
            reverse("expense-group-list"),
            {"name": "Обучение"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ExpenseGroup.objects.filter(
                pk=response.data["id"],
                master=self.master,
            ).exists()
        )

    def test_expense_can_use_global_group(self):
        response = self.client.post(
            reverse("expense-list"),
            {
                "schedule_day": self.schedule_day.pk,
                "group": self.global_group.pk,
                "amount": "500.00",
                "comment": "Перчатки",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Expense.objects.filter(pk=response.data["id"]).exists())

    def test_expense_cannot_use_another_master_group(self):
        another_group = ExpenseGroup.objects.create(
            master=self.another_master,
            name="Обучение",
        )

        response = self.client.post(
            reverse("expense-list"),
            {
                "schedule_day": self.schedule_day.pk,
                "group": another_group.pk,
                "amount": "500.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("group", response.data)

    def test_expense_template_is_created_for_current_master(self):
        response = self.client.post(
            reverse("expense-template-list"),
            {
                "group": self.global_group.pk,
                "amount": "500.00",
                "comment": "Перчатки",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ExpenseTemplate.objects.filter(
                pk=response.data["id"],
                master=self.master,
            ).exists()
        )
