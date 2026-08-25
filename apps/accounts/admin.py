from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import MasterChangeForm, MasterCreationForm
from .models import Master


@admin.register(Master)
class MasterAdmin(UserAdmin):
    add_form = MasterCreationForm
    form = MasterChangeForm
    model = Master
    list_display = ("phone", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("phone", "first_name", "last_name")
    ordering = ("phone",)
    filter_horizontal = ("groups", "user_permissions")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        (
            _("Контактные данные"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_verified",
                    "messenger_max_id",
                )
            },
        ),
        (
            _("Права доступа"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Важные даты"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
