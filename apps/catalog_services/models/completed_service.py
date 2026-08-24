from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Master
from apps.clients.models import Client

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
    price = models.DecimalField(_("Стоимость"), max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)

    class Meta:
        db_table = "completed_services"
        ordering = ("-completed_at",)
        verbose_name = _("Выполненная услуга")
        verbose_name_plural = _("Выполненные услуги")

    def __str__(self):
        return self.service_name
