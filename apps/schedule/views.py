from rest_framework import viewsets

from apps.accounts.models import Master

from .models import (
    AppointmentSlot,
    ScheduleDay,
    ScheduleDayTemplate,
    ScheduleDayTemplateSlot,
)
from .serializers import (
    AppointmentSlotSerializer,
    ScheduleDaySerializer,
    ScheduleDayTemplateSerializer,
    ScheduleDayTemplateSlotSerializer,
)


class ScheduleDayTemplateViewSet(viewsets.ModelViewSet):
    queryset = ScheduleDayTemplate.objects.all()
    serializer_class = ScheduleDayTemplateSerializer
    search_fields = ("name",)
    ordering_fields = ("name", "created_at", "updated_at")
    ordering = ("name",)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ScheduleDayTemplate.objects.none()
        master: Master = self.request.user
        return ScheduleDayTemplate.objects.filter(master=master).prefetch_related("slots")

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)


class ScheduleDayTemplateSlotViewSet(viewsets.ModelViewSet):
    queryset = ScheduleDayTemplateSlot.objects.all()
    serializer_class = ScheduleDayTemplateSlotSerializer
    filterset_fields = ("template", "is_reusable")
    search_fields = ("name",)
    ordering_fields = ("name", "start_time", "end_time", "created_at", "updated_at")
    ordering = ("start_time", "name")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ScheduleDayTemplateSlot.objects.none()
        master: Master = self.request.user
        return ScheduleDayTemplateSlot.objects.filter(master=master).select_related(
            "template"
        )

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)


class ScheduleDayViewSet(viewsets.ModelViewSet):
    queryset = ScheduleDay.objects.all()
    serializer_class = ScheduleDaySerializer
    filterset_fields = {"date": ("exact", "gte", "lte")}
    ordering_fields = ("date",)
    ordering = ("date",)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ScheduleDay.objects.none()
        master: Master = self.request.user
        return ScheduleDay.objects.filter(master=master)

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)


class AppointmentSlotViewSet(viewsets.ModelViewSet):
    queryset = AppointmentSlot.objects.all()
    serializer_class = AppointmentSlotSerializer
    filterset_fields = ("schedule_day", "status", "client")
    search_fields = ("client__name", "client__phone")
    ordering_fields = ("schedule_day__date", "start_time", "end_time", "status")
    ordering = ("schedule_day__date", "start_time")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return AppointmentSlot.objects.none()
        master: Master = self.request.user
        return AppointmentSlot.objects.filter(
            schedule_day__master=master
        ).select_related("schedule_day", "client")
