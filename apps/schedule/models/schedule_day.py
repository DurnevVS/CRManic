from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ScheduleDay(models.Model):
    master = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="schedule_days",
        verbose_name=_("Мастер"),
    )
    date = models.DateField(_("Дата"))

    class Meta:
        db_table = "schedule_days"
        ordering = ("date",)
        verbose_name = _("Рабочий день")
        verbose_name_plural = _("Рабочие дни")
        constraints = (
            models.UniqueConstraint(
                fields=("master", "date"),
                name="unique_schedule_day_per_master",
            ),
        )

    def __str__(self):
        return f"{self.master} — {self.date:%d.%m.%Y}"
