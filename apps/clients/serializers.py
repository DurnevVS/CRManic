from apps.core.api.serializers import ValidatedModelSerializer

from .models import Client


class ClientSerializer(ValidatedModelSerializer):
    class Meta:
        model = Client
        fields = (
            "id",
            "name",
            "phone",
            "phone_verified",
            "messenger_max_id",
            "birthday",
            "comment",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "phone_verified", "created_at", "updated_at")
