from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.accounts.models import Master

from .models import AppointmentSlot, ScheduleDay


def create_master(phone: str) -> Master:
    master = Master(phone=phone)
    master.set_unusable_password()
    master.save()
    return master


class ScheduleAPITests(APITestCase):
    def setUp(self):
        self.master = create_master(phone="+79991234567")
        self.another_master = create_master(phone="+79991234568")
        self.schedule_day = ScheduleDay.objects.create(
            master=self.master,
            date=date(2026, 8, 25),
        )
        token = Token.objects.create(user=self.master)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_schedule_day_is_created_for_current_master(self):
        response = self.client.post(
            reverse("schedule-day-list"),
            {"date": "2026-08-26"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ScheduleDay.objects.filter(
                pk=response.data["id"],
                master=self.master,
            ).exists()
        )

    def test_schedule_day_list_is_scoped_to_master(self):
        ScheduleDay.objects.create(
            master=self.another_master,
            date=date(2026, 8, 25),
        )

        response = self.client.get(reverse("schedule-day-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_overlapping_slot_is_rejected(self):
        AppointmentSlot.objects.create(
            schedule_day=self.schedule_day,
            start_time="10:00",
            end_time="11:00",
        )

        response = self.client.post(
            reverse("appointment-slot-list"),
            {
                "schedule_day": self.schedule_day.pk,
                "start_time": "10:30",
                "end_time": "11:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_time", response.data)

    def test_schedule_day_of_another_master_cannot_be_used(self):
        another_schedule_day = ScheduleDay.objects.create(
            master=self.another_master,
            date=date(2026, 8, 25),
        )

        response = self.client.post(
            reverse("appointment-slot-list"),
            {
                "schedule_day": another_schedule_day.pk,
                "start_time": "10:00",
                "end_time": "11:00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("schedule_day", response.data)
