from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from apps.accounts.models import Master
from apps.schedule.models import ScheduleDay

from .models import Expense, ExpenseGroup


def create_master(phone: str) -> Master:
    master = Master(phone=phone)
    master.set_unusable_password()
    master.save()
    return master


class ExpenseGroupTests(TestCase):
    def test_default_global_groups_exist(self):
        names = set(
            ExpenseGroup.objects.filter(master__isnull=True).values_list(
                "name", flat=True
            )
        )

        self.assertEqual(
            names,
            {"Расходники", "Покупка оборудования", "ТО оборудования"},
        )

    def test_global_group_name_must_be_unique(self):
        ExpenseGroup.objects.create(name="Аренда")

        with self.assertRaises(IntegrityError), transaction.atomic():
            ExpenseGroup.objects.create(name="Аренда")

    def test_personal_group_name_must_be_unique_for_master(self):
        master = create_master(phone="+79991234567")
        ExpenseGroup.objects.create(master=master, name="Обучение")

        with self.assertRaises(IntegrityError), transaction.atomic():
            ExpenseGroup.objects.create(master=master, name="Обучение")

    def test_different_masters_can_use_same_personal_group_name(self):
        first_master = create_master(phone="+79991234567")
        second_master = create_master(phone="+79991234568")

        ExpenseGroup.objects.create(master=first_master, name="Обучение")
        ExpenseGroup.objects.create(master=second_master, name="Обучение")

        self.assertEqual(
            ExpenseGroup.objects.filter(name="Обучение").count(),
            2,
        )


class ExpenseTests(TestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")
        self.schedule_day = ScheduleDay.objects.create(
            master=self.master,
            date=date(2026, 8, 25),
        )

    def test_global_group_is_available_for_expense(self):
        group = ExpenseGroup.objects.get(name="Расходники", master__isnull=True)
        expense = Expense(
            schedule_day=self.schedule_day,
            group=group,
            amount=Decimal("100.00"),
        )

        expense.full_clean()
        expense.save()

        self.assertEqual(expense.group, group)

    def test_master_can_use_personal_group_for_expense(self):
        group = ExpenseGroup.objects.create(master=self.master, name="Обучение")
        expense = Expense(
            schedule_day=self.schedule_day,
            group=group,
            amount=Decimal("100.00"),
        )

        expense.full_clean()
        expense.save()

        self.assertEqual(expense.group, group)

    def test_personal_group_must_belong_to_schedule_day_master(self):
        another_master = create_master(phone="+79991234568")
        group = ExpenseGroup.objects.create(
            master=another_master,
            name="Обучение",
        )
        expense = Expense(
            schedule_day=self.schedule_day,
            group=group,
            amount=Decimal("100.00"),
        )

        with self.assertRaises(ValidationError):
            expense.full_clean()

    def test_amount_must_be_greater_than_zero(self):
        group = ExpenseGroup.objects.get(name="Расходники", master__isnull=True)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Expense.objects.create(
                schedule_day=self.schedule_day,
                group=group,
                amount=Decimal("0.00"),
            )

    def test_used_group_cannot_be_deleted(self):
        group = ExpenseGroup.objects.get(name="Расходники", master__isnull=True)
        Expense.objects.create(
            schedule_day=self.schedule_day,
            group=group,
            amount=Decimal("100.00"),
        )

        with self.assertRaises(ProtectedError):
            group.delete()

    def test_expense_is_deleted_with_schedule_day(self):
        group = ExpenseGroup.objects.get(name="Расходники", master__isnull=True)
        Expense.objects.create(
            schedule_day=self.schedule_day,
            group=group,
            amount=Decimal("100.00"),
        )

        self.schedule_day.delete()

        self.assertFalse(Expense.objects.exists())
