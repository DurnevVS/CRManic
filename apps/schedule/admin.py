from django.contrib import admin

from .models import (
    AppointmentSlot,
    ScheduleDay,
    ScheduleDayTemplate,
    ScheduleDayTemplateSlot,
)


class ScheduleDayTemplateSlotInline(admin.TabularInline):
    model = ScheduleDayTemplateSlot
    extra = 0


@admin.register(ScheduleDayTemplate)
class ScheduleDayTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "master", "created_at")
    search_fields = ("name", "master__phone")
    inlines = (ScheduleDayTemplateSlotInline,)


@admin.register(ScheduleDayTemplateSlot)
class ScheduleDayTemplateSlotAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_time",
        "end_time",
        "template",
        "is_reusable",
        "master",
    )
    list_filter = ("is_reusable",)
    search_fields = ("name", "master__phone", "template__name")


@admin.register(ScheduleDay)
class ScheduleDayAdmin(admin.ModelAdmin):
    list_display = ("date", "master")
    list_filter = ("date",)
    search_fields = ("master__phone",)


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ("schedule_day", "start_time", "end_time", "status", "client")
    list_filter = ("status", "schedule_day__date")
    search_fields = (
        "schedule_day__master__phone",
        "client__name",
        "client__phone",
    )
