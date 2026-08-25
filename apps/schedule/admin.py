from django.contrib import admin

from .models import AppointmentSlot, ScheduleDay


@admin.register(ScheduleDay)
class ScheduleDayAdmin(admin.ModelAdmin):
    list_display = ("date", "master")
    list_filter = ("date",)
    search_fields = ("master__phone",)


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ("schedule_day", "start_time", "end_time")
    list_filter = ("schedule_day__date",)
    search_fields = ("schedule_day__master__phone",)
