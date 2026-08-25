from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounts.models import Master
from apps.clients.models import Client
from apps.core.api.serializers import ValidatedModelSerializer

from .models import CompletedService, Service


class ServiceSerializer(ValidatedModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "price",
            "estimated_material_cost",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CompletedServiceSerializer(ValidatedModelSerializer):
    class Meta:
        model = CompletedService
        fields = (
            "id",
            "client",
            "service",
            "service_name",
            "price",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate_client(self, client: Client):
        master: Master = self.context["request"].user
        if client.master.pk != master.pk:
            raise serializers.ValidationError(_("Клиент принадлежит другому мастеру."))
        return client

    def validate_service(self, service: Service):
        master: Master = self.context["request"].user
        if service.master.pk != master.pk:
            raise serializers.ValidationError(_("Услуга принадлежит другому мастеру."))
        return service
