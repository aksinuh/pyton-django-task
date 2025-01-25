from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
import requests
import random
from django.utils.text import slugify
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.http import JsonResponse
from django.contrib.auth import authenticate, get_user_model
from users.api.serializers import UserRegistrationSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import UserProfileSerializer
from rest_framework.permissions import AllowAny
from django.conf import settings


User = get_user_model()

class RegisterAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
        
        return Response(response_data, status=201)


class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "message": "Login uğurludur.",
                "tokens": serializer.validated_data["tokens"]
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    

class GoogleLoginView(APIView):
    def post(self, request):
        google_token = request.data.get("token")
        if not google_token:
            return Response({"error": "Google token is required."}, status=400)

        google_url = "https://www.googleapis.com/oauth2/v3/tokeninfo"
        response = requests.get(google_url, params={"id_token": google_token})
        if response.status_code != 200:
            return Response({"error": "Invalid Google token."}, status=400)

        user_data = response.json()
        email = user_data.get("email")
        first_name = user_data.get("given_name", "")
        last_name = user_data.get("family_name", "")

        if not email:
            return Response({"error": "Google token does not contain email."}, status=400)

        base_username = slugify(email.split('@')[0])
        username = base_username
        while User.objects.filter(username=username).exists():
            random_number = random.randint(1000, 9999)
            username = f"{base_username}_{random_number}"

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }
        )

        if not user:
            return Response({"detail": "User not found", "code": "user_not_found"}, status=400)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=200)