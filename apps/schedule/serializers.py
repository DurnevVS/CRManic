from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounts.models import Master
from apps.clients.models import Client
from apps.core.api.serializers import ValidatedModelSerializer

from .models import (
    AppointmentSlot,
    AppointmentSlotStatus,
    ScheduleDay,
    ScheduleDayTemplate,
    ScheduleDayTemplateSlot,
)


class ScheduleDayTemplateSlotSerializer(ValidatedModelSerializer):
    class Meta:
        model = ScheduleDayTemplateSlot
        fields = (
            "id",
            "template",
            "name",
            "start_time",
            "end_time",
            "is_reusable",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_template(self, template: ScheduleDayTemplate | None):
        if template is None:
            return template

        master: Master = self.context["request"].user
        if template.master_id != master.pk:
            raise serializers.ValidationError(
                _("Шаблон рабочего дня принадлежит другому мастеру.")
            )
        return template


class ScheduleDayTemplateSerializer(ValidatedModelSerializer):
    slots = ScheduleDayTemplateSlotSerializer(many=True, read_only=True)

    class Meta:
        model = ScheduleDayTemplate
        fields = ("id", "name", "slots", "created_at", "updated_at")
        read_only_fields = ("id", "slots", "created_at", "updated_at")


class ScheduleDaySerializer(ValidatedModelSerializer):
    class Meta:
        model = ScheduleDay
        fields = ("id", "date")
        read_only_fields = ("id",)


class AppointmentSlotSerializer(ValidatedModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = AppointmentSlot
        fields = (
            "id",
            "schedule_day",
            "start_time",
            "end_time",
            "client",
            "status",
            "status_display",
        )
        read_only_fields = ("id", "status_display")

    def get_status_display(self, slot: AppointmentSlot) -> str:
        return str(AppointmentSlotStatus(slot.status).label)

    def validate_schedule_day(self, schedule_day: ScheduleDay):
        master: Master = self.context["request"].user
        if schedule_day.master.pk != master.pk:
            raise serializers.ValidationError(
                _("Рабочий день принадлежит другому мастеру.")
            )
        return schedule_day

    def validate_client(self, client: Client):
        master: Master = self.context["request"].user
        if client.master.pk != master.pk:
            raise serializers.ValidationError(_("Клиент принадлежит другому мастеру."))
        return client
