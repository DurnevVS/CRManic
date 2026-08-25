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

        errors = {}
        if self.status == AppointmentSlotStatus.AVAILABLE:
            if self.client_id is not None:
                errors["client"] = _("У свободного окошка не должно быть клиента.")
        elif self.client_id is None:
            errors["client"] = _(
                "Для несвободного окошка необходимо выбрать клиента."
            )
        elif self.schedule_day_id is not None:
            client: Client = self.client
            schedule_day: ScheduleDay = self.schedule_day
            if client.master.pk != schedule_day.master.pk:
                errors["client"] = _(
                    "Клиент и рабочий день должны принадлежать одному мастеру."
                )

        if (
            self.schedule_day_id is not None
            and self.start_time is not None
            and self.end_time is not None
        ):
            overlapping_slots = AppointmentSlot.objects.filter(
                schedule_day_id=self.schedule_day_id,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            )
            if self.pk is not None:
                overlapping_slots = overlapping_slots.exclude(pk=self.pk)

            if overlapping_slots.exists():
                errors["start_time"] = _(
                    "Окошко пересекается с другим окошком рабочего дня."
                )
                errors["end_time"] = _(
                    "Окошко пересекается с другим окошком рабочего дня."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.schedule_day}: {self.start_time:%H:%M}–{self.end_time:%H:%M}"
