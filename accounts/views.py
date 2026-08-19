from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.serializers import AuthUserSerializer, LoginSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"].strip()
        password = serializer.validated_data["password"]

        login_identifier = username
        if username.isdigit():
            matched_user = User.objects.filter(mobile_number=username).first()
            if matched_user:
                login_identifier = matched_user.username

        user = authenticate(request, username=login_identifier, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid username/mobile number or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "This account has been disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": AuthUserSerializer(user).data,
                "accessToken": str(refresh.access_token),
                "refreshToken": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
