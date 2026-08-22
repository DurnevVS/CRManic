from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

phone_validator = RegexValidator(
    regex=r"^\+[1-9]\d{7,14}$",
    message=_(
        "Номер телефона должен быть в международном формате, например +79991234567."
    ),
)


class ContactInfo(models.Model):
    phone = models.CharField(
        _("Номер телефона"), max_length=32, validators=[phone_validator]
    )
    phone_verified = models.BooleanField(_("Номер телефона подтвержден"), default=True)
    messenger_max_id = models.BigIntegerField(_("ID в MAX"), null=True, blank=True)

    # TODO Добавить функцию подтверждения номера телефона через мессенджеры

    class Meta:
        abstract = True
