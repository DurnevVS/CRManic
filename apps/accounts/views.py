from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Master
from .serializers import (
    MasterSerializer,
    TokenRequestSerializer,
    TokenResponseSerializer,
)


class TokenView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        request=TokenRequestSerializer,
        responses={status.HTTP_200_OK: TokenResponseSerializer},
        tags=("Аутентификация",),
    )
    def post(self, request):
        serializer = TokenRequestSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user: Master = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class LogoutView(APIView):
    @extend_schema(
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
        tags=("Аутентификация",),
    )
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MasterSerializer

    def get_object(self):
        return self.request.user
