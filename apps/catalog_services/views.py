from rest_framework import viewsets

from apps.accounts.models import Master

from .models import CompletedService, Service
from .serializers import CompletedServiceSerializer, ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filterset_fields = ("is_active",)
    search_fields = ("name", "description")
    ordering_fields = ("name", "price", "created_at", "updated_at")
    ordering = ("name",)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Service.objects.none()
        master: Master = self.request.user
        return Service.objects.filter(master=master)

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)


class CompletedServiceViewSet(viewsets.ModelViewSet):
    queryset = CompletedService.objects.all()
    serializer_class = CompletedServiceSerializer
    filterset_fields = ("client", "service")
    search_fields = ("service_name", "client__name", "client__phone")
    ordering_fields = ("service_name", "price", "created_at")
    ordering = ("-created_at",)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CompletedService.objects.none()
        master: Master = self.request.user
        return CompletedService.objects.filter(master=master).select_related(
            "client",
            "service",
        )

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)
