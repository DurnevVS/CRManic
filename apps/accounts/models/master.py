from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .contact_info import ContactInfo, phone_validator
from .manager import MasterManager


class Master(AbstractUser, ContactInfo):
    phone = models.CharField(
        _("Номер телефона"), max_length=32, unique=True, validators=[phone_validator]
    )

    username = None
    email = None

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ()

    objects = MasterManager()

    class Meta:
        db_table = "users"
        verbose_name = _("Мастер")
        verbose_name_plural = _("Мастера")
