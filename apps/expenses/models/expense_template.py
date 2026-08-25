from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Master
from apps.core.models.fields import expense_field

from .expense_group import ExpenseGroup


class ExpenseTemplate(models.Model):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="expense_templates",
        verbose_name=_("Мастер"),
    )
    group = models.ForeignKey(
        ExpenseGroup,
        on_delete=models.PROTECT,
        related_name="expense_templates",
        verbose_name=_("Группа расходов"),
    )
    amount = expense_field(_("Сумма"))
    comment = models.TextField(_("Комментарий"), blank=True)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата изменения"), auto_now=True)

    class Meta:
        db_table = "expense_templates"
        ordering = ("group__name", "amount")
        verbose_name = _("Шаблон расхода")
        verbose_name_plural = _("Шаблоны расходов")
        constraints = (
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="expense_template_amount_greater_than_zero",
            ),
        )

    def clean(self):
        super().clean()

        if self.group_id is None or self.master_id is None:
            return

        group: ExpenseGroup = self.group
        group_master: Master | None = group.master
        if group_master is not None and group_master.pk != self.master.pk:
            raise ValidationError({
                "group": _(
                    "Личная группа расходов и шаблон должны принадлежать "
                    "одному мастеру."
                )
            })

    def __str__(self):
        if self.comment:
            return f"{self.group} — {self.comment} — {self.amount}"
        return f"{self.group} — {self.amount}"
