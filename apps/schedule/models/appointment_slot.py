from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.clients.models import Client

from .schedule_day import ScheduleDay


class AppointmentSlotStatus(models.IntegerChoices):
    AVAILABLE = 1, _("Свободно")
    BOOKED = 2, _("Клиент записан")
    COMPLETED = 3, _("Выполнено")
    CANCELLED = 0, _("Отменено / клиент не пришёл")


class AppointmentSlot(models.Model):
    schedule_day = models.ForeignKey(
        ScheduleDay,
        on_delete=models.CASCADE,
        related_name="appointment_slots",
        verbose_name=_("Рабочий день"),
    )
    start_time = models.TimeField(_("Время начала"))
    end_time = models.TimeField(_("Время окончания"))
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="appointment_slots",
        verbose_name=_("Клиент"),
    )
    status = models.PositiveSmallIntegerField(
        _("Статус"),
        choices=AppointmentSlotStatus.choices,
        default=AppointmentSlotStatus.AVAILABLE,
    )

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
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status=AppointmentSlotStatus.AVAILABLE,
                        client__isnull=True,
                    )
                    | models.Q(
                        status__in=(
                            AppointmentSlotStatus.BOOKED,
                            AppointmentSlotStatus.COMPLETED,
                            AppointmentSlotStatus.CANCELLED,
                        ),
                        client__isnull=False,
                    )
                ),
                name="appointment_slot_status_matches_client",
            ),
        )

    def clean(self):
        super().clean()

        if self.status == AppointmentSlotStatus.AVAILABLE:
            if self.client_id is not None:
                raise ValidationError({
                    "client": _("У свободного окошка не должно быть клиента.")
                })
            return

        if self.client_id is None:
            raise ValidationError({
                "client": _("Для несвободного окошка необходимо выбрать клиента.")
            })

        if self.schedule_day_id is None:
            return

        client: Client = self.client
        schedule_day: ScheduleDay = self.schedule_day
        if client.master.pk != schedule_day.master.pk:
            raise ValidationError({
                "client": _("Клиент и рабочий день должны принадлежать одному мастеру.")
            })

    def __str__(self):
        return f"{self.schedule_day}: {self.start_time:%H:%M}–{self.end_time:%H:%M}"
