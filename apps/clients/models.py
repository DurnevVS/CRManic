from datetime import date

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import ContactInfo, Master


class Client(ContactInfo):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="clients",
        verbose_name=_("Мастер"),
    )

    name = models.CharField(_("Имя"), max_length=255)
    birthday = models.DateField(
        _("Дата рождения"),
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(
                date.today,
                message=_("Дата рождения не может быть в будущем."),
            )
        ],
    )
    comment = models.TextField(_("Комментарий"), blank=True)
    is_active = models.BooleanField(_("Активен"), default=True)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата изменения"), auto_now=True)

    class Meta:
        db_table = "clients"
        ordering = ("name",)
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")

        constraints = (
            models.UniqueConstraint(
                fields=["master", "phone"],
                name="unique_client_phone_per_master",
            ),
        )

    def __str__(self):
        return self.name
