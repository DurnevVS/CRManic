from django.contrib import admin

from .models import Expense, ExpenseGroup


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "master", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "master__phone")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("schedule_day", "group", "amount", "created_at")
    list_filter = ("group", "schedule_day__date")
    search_fields = (
        "group__name",
        "schedule_day__master__phone",
        "comment",
    )
