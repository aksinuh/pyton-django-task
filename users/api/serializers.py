from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import ModelSerializer
from django.utils import timezone
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        # Şifrəni hash edərək istifadəçi yaradın
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
    
        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Daxil edilmiş username və email mövcud deyil.")

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Yanlış parol.")

        user.last_login = timezone.now()
        user.save()

        refresh = RefreshToken.for_user(user)
        data["tokens"] = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return data
    
    
class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']