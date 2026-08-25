from django.db.models import Q
from rest_framework import permissions, viewsets

from apps.accounts.models import Master

from .models import Expense, ExpenseGroup, ExpenseTemplate
from .permissions import ExpenseGroupPermission
from .serializers import (
    ExpenseGroupSerializer,
    ExpenseSerializer,
    ExpenseTemplateSerializer,
)


class ExpenseGroupViewSet(viewsets.ModelViewSet):
    queryset = ExpenseGroup.objects.all()
    serializer_class = ExpenseGroupSerializer
    permission_classes = (permissions.IsAuthenticated, ExpenseGroupPermission)
    search_fields = ("name",)
    ordering_fields = ("name", "created_at", "updated_at")
    ordering = ("name",)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ExpenseGroup.objects.none()
        master: Master = self.request.user
        return ExpenseGroup.objects.filter(
            Q(master=master) | Q(master__isnull=True)
        ).select_related("master")

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filterset_fields = ("schedule_day", "group")
    search_fields = ("group__name", "comment")
    ordering_fields = ("schedule_day__date", "amount", "created_at", "updated_at")
    ordering = ("-schedule_day__date", "-created_at")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Expense.objects.none()
        master: Master = self.request.user
        return Expense.objects.filter(schedule_day__master=master).select_related(
            "schedule_day",
            "group",
        )


class ExpenseTemplateViewSet(viewsets.ModelViewSet):
    queryset = ExpenseTemplate.objects.all()
    serializer_class = ExpenseTemplateSerializer
    filterset_fields = ("group",)
    search_fields = ("group__name", "comment")
    ordering_fields = ("group__name", "amount", "created_at", "updated_at")
    ordering = ("group__name", "amount")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ExpenseTemplate.objects.none()
        master: Master = self.request.user
        return ExpenseTemplate.objects.filter(master=master).select_related("group")

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)
