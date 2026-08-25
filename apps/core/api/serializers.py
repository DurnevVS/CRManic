from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from rest_framework import serializers


class ValidatedModelSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        model = self.Meta.model
        instance = model(**validated_data)
        self._full_clean(instance)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for field_name, value in validated_data.items():
            setattr(instance, field_name, value)

        self._full_clean(instance)
        instance.save()
        return instance

    def _full_clean(self, instance: models.Model):
        try:
            instance.full_clean()
        except DjangoValidationError as error:
            try:
                detail = error.message_dict
            except AttributeError:
                detail = {"non_field_errors": error.messages}
            raise serializers.ValidationError(detail) from error
