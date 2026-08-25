from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Master
from apps.core.models.fields import expense_field
from apps.schedule.models import ScheduleDay

from .expense_group import ExpenseGroup


class Expense(models.Model):
    schedule_day = models.ForeignKey(
        ScheduleDay,
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name=_("Рабочий день"),
    )
    group = models.ForeignKey(
        ExpenseGroup,
        on_delete=models.PROTECT,
        related_name="expenses",
        verbose_name=_("Группа расходов"),
    )
    amount = expense_field(_("Сумма"))
    comment = models.TextField(_("Комментарий"), blank=True)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата изменения"), auto_now=True)

    class Meta:
        db_table = "expenses"
        ordering = ("-schedule_day__date", "-created_at")
        verbose_name = _("Расход")
        verbose_name_plural = _("Расходы")
        constraints = (
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="expense_amount_greater_than_zero",
            ),
        )

    def clean(self):
        super().clean()

        if self.group_id is None or self.schedule_day_id is None:
            return

        group: ExpenseGroup = self.group
        group_master: Master | None = group.master
        if group_master is None:
            return

        schedule_day = self.schedule_day
        schedule_day_master = schedule_day.master
        if group_master.pk != schedule_day_master.pk:
            raise ValidationError({
                "group": _(
                    "Личная группа расходов и рабочий день должны принадлежать "
                    "одному мастеру."
                )
            })

    def __str__(self):
        return f"{self.group}: {self.amount}"
