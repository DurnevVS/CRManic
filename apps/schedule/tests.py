from datetime import date, time

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import Master
from apps.clients.models import Client

from .models import (
    AppointmentSlot,
    AppointmentSlotStatus,
    ScheduleDay,
    ScheduleDayTemplate,
    ScheduleDayTemplateSlot,
)


def create_master(phone: str) -> Master:
    master = Master(phone=phone)
    master.set_unusable_password()
    master.save()
    return master


def create_client(master: Master, phone: str = "+79991234568") -> Client:
    return Client.objects.create(master=master, name="Клиент", phone=phone)


class ScheduleDayTests(TestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")

    def test_master_cannot_have_two_schedule_days_for_same_date(self):
        schedule_date = date(2026, 8, 25)
        ScheduleDay.objects.create(master=self.master, date=schedule_date)

        with self.assertRaises(IntegrityError), transaction.atomic():
            ScheduleDay.objects.create(master=self.master, date=schedule_date)


class ScheduleDayTemplateSlotTests(TestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")
        self.template = ScheduleDayTemplate.objects.create(
            master=self.master,
            name="Обычный день",
        )

    def test_standalone_slot_must_be_reusable(self):
        slot = ScheduleDayTemplateSlot(
            master=self.master,
            name="Окошко с 9 утра",
            start_time=time(9),
            end_time=time(10),
        )

        with self.assertRaises(ValidationError):
            slot.full_clean()

    def test_reusable_slot_can_exist_without_day_template(self):
        slot = ScheduleDayTemplateSlot(
            master=self.master,
            name="Окошко с 9 утра",
            start_time=time(9),
            end_time=time(10),
            is_reusable=True,
        )

        slot.full_clean()

    def test_slot_and_day_template_must_belong_to_same_master(self):
        another_master = create_master(phone="+79991234568")
        slot = ScheduleDayTemplateSlot(
            master=another_master,
            template=self.template,
            name="Окошко",
            start_time=time(9),
            end_time=time(10),
        )

        with self.assertRaises(ValidationError):
            slot.full_clean()

    def test_slots_in_day_template_cannot_overlap(self):
        ScheduleDayTemplateSlot.objects.create(
            master=self.master,
            template=self.template,
            name="Первое окошко",
            start_time=time(9),
            end_time=time(10),
        )
        slot = ScheduleDayTemplateSlot(
            master=self.master,
            template=self.template,
            name="Второе окошко",
            start_time=time(9, 30),
            end_time=time(10, 30),
        )

        with self.assertRaises(ValidationError):
            slot.full_clean()


class AppointmentSlotTests(TestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")
        self.schedule_day = ScheduleDay.objects.create(
            master=self.master,
            date=date(2026, 8, 25),
        )

    def test_new_slot_is_available(self):
        slot = AppointmentSlot.objects.create(
            schedule_day=self.schedule_day,
            start_time=time(10),
            end_time=time(11),
        )

        self.assertEqual(slot.status, AppointmentSlotStatus.AVAILABLE)
        self.assertIsNone(slot.client)

    def test_available_slot_cannot_have_client(self):
        slot = AppointmentSlot(
            schedule_day=self.schedule_day,
            start_time=time(10),
            end_time=time(11),
            client=create_client(self.master),
        )

        with self.assertRaises(ValidationError):
            slot.full_clean()

    def test_non_available_slot_requires_client(self):
        statuses = (
            AppointmentSlotStatus.BOOKED,
            AppointmentSlotStatus.COMPLETED,
            AppointmentSlotStatus.CANCELLED,
        )

        for status in statuses:
            with self.subTest(status=status):
                slot = AppointmentSlot(
                    schedule_day=self.schedule_day,
                    start_time=time(10),
                    end_time=time(11),
                    status=status,
                )

                with self.assertRaises(ValidationError):
                    slot.full_clean()

    def test_client_and_schedule_day_must_belong_to_same_master(self):
        another_master = create_master(phone="+79991234569")
        slot = AppointmentSlot(
            schedule_day=self.schedule_day,
            start_time=time(10),
            end_time=time(11),
            status=AppointmentSlotStatus.BOOKED,
            client=create_client(another_master),
        )

        with self.assertRaises(ValidationError):
            slot.full_clean()

    def test_end_time_must_be_after_start_time(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            AppointmentSlot.objects.create(
                schedule_day=self.schedule_day,
                start_time=time(12),
                end_time=time(11),
            )

    def test_slot_period_must_be_unique_within_schedule_day(self):
        slot_data = {
            "schedule_day": self.schedule_day,
            "start_time": time(10),
            "end_time": time(11),
        }
        AppointmentSlot.objects.create(**slot_data)

        with self.assertRaises(IntegrityError), transaction.atomic():
            AppointmentSlot.objects.create(**slot_data)

    def test_slots_cannot_overlap(self):
        AppointmentSlot.objects.create(
            schedule_day=self.schedule_day,
            start_time=time(10),
            end_time=time(11),
        )
        overlapping_slot = AppointmentSlot(
            schedule_day=self.schedule_day,
            start_time=time(10, 30),
            end_time=time(11, 30),
        )

        with self.assertRaises(ValidationError):
            overlapping_slot.full_clean()

    def test_adjacent_slots_do_not_overlap(self):
        AppointmentSlot.objects.create(
            schedule_day=self.schedule_day,
            start_time=time(10),
            end_time=time(11),
        )
        adjacent_slot = AppointmentSlot(
            schedule_day=self.schedule_day,
            start_time=time(11),
            end_time=time(12),
        )

        adjacent_slot.full_clean()

    def test_slot_does_not_overlap_itself_when_updated(self):
        slot = AppointmentSlot.objects.create(
            schedule_day=self.schedule_day,
            start_time=time(10),
            end_time=time(11),
        )

        slot.full_clean()
