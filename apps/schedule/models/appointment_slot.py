from django.db import models
from django.utils.translation import gettext_lazy as _

from .schedule_day import ScheduleDay


class AppointmentSlot(models.Model):
    schedule_day = models.ForeignKey(
        ScheduleDay,
        on_delete=models.CASCADE,
        related_name="appointment_slots",
        verbose_name=_("Рабочий день"),
    )
    start_time = models.TimeField(_("Время начала"))
    end_time = models.TimeField(_("Время окончания"))

    class Meta:
        db_table = "appointment_slots"
        ordering = ("schedule_day__date", "start_time")
        verbose_name = _("Окошко для записи")
        verbose_name_plural = _("Окошки для записи")
        constraints = (
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="appointment_slot_end_after_start",
            ),
            models.UniqueConstraint(
                fields=("schedule_day", "start_time", "end_time"),
                name="unique_appointment_slot_period_per_day",
            ),
        )

    def __str__(self):
        return f"{self.schedule_day}: {self.start_time:%H:%M}–{self.end_time:%H:%M}"
