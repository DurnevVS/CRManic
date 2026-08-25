from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounts.models import Master
from apps.core.api.serializers import ValidatedModelSerializer
from apps.schedule.models import ScheduleDay

from .models import Expense, ExpenseGroup, ExpenseTemplate


def validate_group_owner(group: ExpenseGroup, master: Master):
    group_master: Master | None = group.master
    if group_master is not None and group_master.pk != master.pk:
        raise serializers.ValidationError(
            _("Группа расходов принадлежит другому мастеру.")
        )
    return group


class ExpenseGroupSerializer(ValidatedModelSerializer):
    is_global = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseGroup
        fields = ("id", "name", "is_global", "created_at", "updated_at")
        read_only_fields = ("id", "is_global", "created_at", "updated_at")

    def get_is_global(self, group: ExpenseGroup) -> bool:
        return group.master is None


class ExpenseSerializer(ValidatedModelSerializer):
    class Meta:
        model = Expense
        fields = (
            "id",
            "schedule_day",
            "group",
            "amount",
            "comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_schedule_day(self, schedule_day: ScheduleDay):
        master: Master = self.context["request"].user
        if schedule_day.master.pk != master.pk:
            raise serializers.ValidationError(
                _("Рабочий день принадлежит другому мастеру.")
            )
        return schedule_day

    def validate_group(self, group: ExpenseGroup):
        master: Master = self.context["request"].user
        return validate_group_owner(group, master)


class ExpenseTemplateSerializer(ValidatedModelSerializer):
    class Meta:
        model = ExpenseTemplate
        fields = (
            "id",
            "group",
            "amount",
            "comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_group(self, group: ExpenseGroup):
        master: Master = self.context["request"].user
        return validate_group_owner(group, master)
