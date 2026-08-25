from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "master", "birthday", "is_active")
    list_filter = ("is_active", "master")
    search_fields = ("name", "phone", "master__phone")
    readonly_fields = ("created_at", "updated_at")
