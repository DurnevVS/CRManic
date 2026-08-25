from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Master


class ExpenseGroup(models.Model):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="expense_groups",
        verbose_name=_("Мастер"),
    )
    name = models.CharField(_("Название"), max_length=255)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата изменения"), auto_now=True)

    class Meta:
        db_table = "expense_groups"
        ordering = ("name",)
        verbose_name = _("Группа расходов")
        verbose_name_plural = _("Группы расходов")
        constraints = (
            models.UniqueConstraint(
                fields=("name",),
                condition=models.Q(master__isnull=True),
                name="unique_global_expense_group_name",
            ),
            models.UniqueConstraint(
                fields=("master", "name"),
                condition=models.Q(master__isnull=False),
                name="unique_expense_group_name_per_master",
            ),
        )

    def __str__(self):
        return self.name
