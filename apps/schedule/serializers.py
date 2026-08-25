from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounts.models import Master
from apps.clients.models import Client
from apps.core.api.serializers import ValidatedModelSerializer

from .models import AppointmentSlot, AppointmentSlotStatus, ScheduleDay


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
