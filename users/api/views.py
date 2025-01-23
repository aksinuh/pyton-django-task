from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.http import JsonResponse
from django.contrib.auth import authenticate, get_user_model
from users.api.serializers import UserRegistrationSerializer


User = get_user_model()

class RegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            token_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            response_data = {
                "user": serializer.data,
                "tokens": token_data,
            }
            return JsonResponse(data=response_data, safe=False, status=status.HTTP_201_CREATED)

        return JsonResponse(data=serializer.errors, safe=False, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.query_params.get("username")
        email = request.query_params.get("email")
        password = request.query_params.get("password")

        if not username or not email or not password:
            return Response({"error": "Username, email və password daxil edilməlidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            return Response({"error": "Daxil edilmiş username və email mövcud deyil."}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            token_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response({"message": "Login uğurludur.", "tokens": token_data}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Yanlış password."}, status=status.HTTP_401_UNAUTHORIZED)