from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Master
from apps.clients.models import Client
from apps.core.models.fields import price_field

from .service import Service


class CompletedService(models.Model):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="completed_services",
        verbose_name=_("Мастер"),
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="completed_services",
        verbose_name=_("Клиент"),
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completed_services",
        verbose_name=_("Услуга"),
    )

    service_name = models.CharField(_("Название услуги"), max_length=255)
    price = price_field(_("Стоимость"))
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)

    class Meta:
        db_table = "completed_services"
        ordering = ("-created_at",)
        verbose_name = _("Выполненная услуга")
        verbose_name_plural = _("Выполненные услуги")
        constraints = (
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="completed_service_price_non_negative",
            ),
        )

    def clean(self):
        super().clean()

        if self.master_id is None or self.client_id is None:
            return

        errors = {}
        if self.client.master.pk != self.master.pk:
            errors["client"] = _(
                "Клиент и выполненная услуга должны принадлежать одному мастеру."
            )

        if self.service_id is not None:
            service: Service = self.service
            if service.master.pk != self.master.pk:
                errors["service"] = _(
                    "Услуга и выполненная услуга должны принадлежать одному мастеру."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.service_name
