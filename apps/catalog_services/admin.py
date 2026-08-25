from django.contrib import admin

from .models import CompletedService, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "master", "price", "is_active", "updated_at")
    list_filter = ("is_active", "master")
    search_fields = ("name", "master__phone", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CompletedService)
class CompletedServiceAdmin(admin.ModelAdmin):
    list_display = ("service_name", "client", "master", "price", "created_at")
    list_filter = ("master", "service", "created_at")
    search_fields = (
        "service_name",
        "client__name",
        "client__phone",
        "master__phone",
    )
    readonly_fields = ("created_at",)
