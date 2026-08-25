from django.contrib import admin

from .models import Expense, ExpenseGroup, ExpenseTemplate


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "master")
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


@admin.register(ExpenseTemplate)
class ExpenseTemplateAdmin(admin.ModelAdmin):
    list_display = ("group", "comment", "amount", "master")
    list_filter = ("group",)
    search_fields = ("group__name", "master__phone", "comment")
