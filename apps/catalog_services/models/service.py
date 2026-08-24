from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.fields import expense_field, price_field


class Service(models.Model):
    master = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name=_("Мастер"),
    )

    name = models.CharField(_("Название"), max_length=255)
    price = price_field(_("Стоимость"))

    estimated_material_cost = expense_field(
        _("Примерная стоимость расходников"), nullable=True
    )

    description = models.TextField(_("Описание"), blank=True)
    is_active = models.BooleanField(_("Активна"), default=True)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата изменения"), auto_now=True)

    class Meta:
        db_table = "services"
        ordering = ("name",)
        verbose_name = _("Услуга")
        verbose_name_plural = _("Услуги")

        constraints = [
            models.UniqueConstraint(
                fields=("master", "name"),
                name="unique_service_name_per_master",
            )
        ]

    def __str__(self):
        return self.name
