from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import LogoutView, MeView, TokenView
from apps.catalog_services.views import CompletedServiceViewSet, ServiceViewSet
from apps.clients.views import ClientViewSet
from apps.expenses.views import ExpenseGroupViewSet, ExpenseTemplateViewSet, ExpenseViewSet
from apps.schedule.views import (
    AppointmentSlotViewSet,
    ScheduleDayTemplateSlotViewSet,
    ScheduleDayTemplateViewSet,
    ScheduleDayViewSet,
)

router = DefaultRouter()
router.register("clients", ClientViewSet, basename="client")
router.register("services", ServiceViewSet, basename="service")
router.register(
    "completed-services",
    CompletedServiceViewSet,
    basename="completed-service",
)
router.register("schedule-days", ScheduleDayViewSet, basename="schedule-day")
router.register(
    "schedule-day-templates",
    ScheduleDayTemplateViewSet,
    basename="schedule-day-template",
)
router.register(
    "schedule-day-template-slots",
    ScheduleDayTemplateSlotViewSet,
    basename="schedule-day-template-slot",
)
router.register(
    "appointment-slots",
    AppointmentSlotViewSet,
    basename="appointment-slot",
)
router.register("expense-groups", ExpenseGroupViewSet, basename="expense-group")
router.register("expenses", ExpenseViewSet, basename="expense")
router.register(
    "expense-templates",
    ExpenseTemplateViewSet,
    basename="expense-template",
)

urlpatterns = [
    path("auth/token/", TokenView.as_view(), name="auth-token"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
