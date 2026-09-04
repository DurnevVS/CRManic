from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Master

from .schedule_day_template import ScheduleDayTemplate


class ScheduleDayTemplateSlot(models.Model):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="schedule_day_template_slots",
        verbose_name=_("Мастер"),
    )
    template = models.ForeignKey(
        ScheduleDayTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="slots",
        verbose_name=_("Шаблон рабочего дня"),
    )
    name = models.CharField(_("Название"), max_length=255)
    start_time = models.TimeField(_("Время начала"))
    end_time = models.TimeField(_("Время окончания"))
    is_reusable = models.BooleanField(
        _("Сохранено для повторного использования"),
        default=False,
    )
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата изменения"), auto_now=True)

    class Meta:
        db_table = "schedule_day_template_slots"
        ordering = ("start_time", "name")
        verbose_name = _("Шаблон окошка")
        verbose_name_plural = _("Шаблоны окошек")
        constraints = (
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="schedule_day_template_slot_end_after_start",
            ),
            models.UniqueConstraint(
                fields=("template", "start_time", "end_time"),
                name="unique_slot_period_per_schedule_day_template",
            ),
            models.UniqueConstraint(
                fields=("master", "name"),
                condition=models.Q(is_reusable=True),
                name="unique_reusable_slot_template_name_per_master",
            ),
        )

    def clean(self):
        super().clean()

        errors = {}
        if self.template_id is None and not self.is_reusable:
            errors["is_reusable"] = _(
                "Окошко без шаблона рабочего дня должно быть сохранено "
                "для повторного использования."
            )

        template: ScheduleDayTemplate | None = None
        if self.template_id is not None:
            template = self.template

        if (
            template is not None
            and self.master_id is not None
            and template.master_id != self.master_id
        ):
            errors["template"] = _(
                "Шаблон рабочего дня принадлежит другому мастеру."
            )

        if (
            self.template_id is not None
            and self.start_time is not None
            and self.end_time is not None
        ):
            overlapping_slots = ScheduleDayTemplateSlot.objects.filter(
                template_id=self.template_id,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            )
            if self.pk is not None:
                overlapping_slots = overlapping_slots.exclude(pk=self.pk)

            if overlapping_slots.exists():
                message = _("Окошко пересекается с другим окошком шаблона.")
                errors["start_time"] = message
                errors["end_time"] = message

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.name}: {self.start_time:%H:%M}–{self.end_time:%H:%M}"
