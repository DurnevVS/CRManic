from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Master


class ScheduleDayTemplate(models.Model):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="schedule_day_templates",
        verbose_name=_("Мастер"),
    )
    name = models.CharField(_("Название"), max_length=255)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата изменения"), auto_now=True)

    class Meta:
        db_table = "schedule_day_templates"
        ordering = ("name",)
        verbose_name = _("Шаблон рабочего дня")
        verbose_name_plural = _("Шаблоны рабочих дней")
        constraints = (
            models.UniqueConstraint(
                fields=("master", "name"),
                name="unique_schedule_day_template_name_per_master",
            ),
        )

    def __str__(self):
        return self.name
