from datetime import date, time

from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import Master

from .models import AppointmentSlot, ScheduleDay


def create_master(phone: str) -> Master:
    master = Master(phone=phone)
    master.set_unusable_password()
    master.save()
    return master


class ScheduleDayTests(TestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")

    def test_master_cannot_have_two_schedule_days_for_same_date(self):
        schedule_date = date(2026, 8, 25)
        ScheduleDay.objects.create(master=self.master, date=schedule_date)

        with self.assertRaises(IntegrityError), transaction.atomic():
            ScheduleDay.objects.create(master=self.master, date=schedule_date)


class AppointmentSlotTests(TestCase):
    def setUp(self):
        master = create_master(phone="+79991234567")
        self.schedule_day = ScheduleDay.objects.create(
            master=master,
            date=date(2026, 8, 25),
        )

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
