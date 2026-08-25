from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import Master

from .models import Client


class ClientValidationTests(TestCase):
    def setUp(self):
        self.master = Master(phone="+79991234567")
        self.master.set_unusable_password()
        self.master.save()

    def test_birthday_cannot_be_in_future(self):
        client = Client(
            master=self.master,
            name="Клиент",
            phone="+79991234568",
            birthday=date.today() + timedelta(days=1),
        )

        with self.assertRaises(ValidationError):
            client.full_clean()
