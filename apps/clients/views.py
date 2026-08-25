from rest_framework import viewsets

from apps.accounts.models import Master

from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filterset_fields = ("is_active",)
    search_fields = ("name", "phone")
    ordering_fields = ("name", "birthday", "created_at", "updated_at")
    ordering = ("name",)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Client.objects.none()
        master: Master = self.request.user
        return Client.objects.filter(master=master)

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)
