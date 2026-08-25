from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.core.api.serializers import ValidatedModelSerializer

from .models import Master


class MasterSerializer(ValidatedModelSerializer):
    class Meta:
        model = Master
        fields = (
            "id",
            "phone",
            "phone_verified",
            "first_name",
            "last_name",
            "messenger_max_id",
            "date_joined",
        )
        read_only_fields = ("id", "phone", "phone_verified", "date_joined")


class TokenRequestSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        request = self.context.get("request")
        user = authenticate(
            request=request,
            phone=attrs["phone"],
            password=attrs["password"],
        )
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": [_("Неверный номер телефона или пароль.")]}
            )

        attrs["user"] = user
        return attrs


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
