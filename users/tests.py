from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

User = get_user_model()

class AuthTests(APITestCase):
    
    def setUp(self):
        self.register_url = "/api/register/" 
        self.login_url = "/api/login/"  
        self.google_login_url = "/api/google-login/"  
        self.profile_url = "/api/profile/"  
        self.test_username = "testuser"
        self.test_email = "testuser@gmail.com"
        self.test_password = "testpassword123"

        self.user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password,
        )

    def test_user_registration(self):
        """İstifadəçi qeydiyyatını test edir."""
        data = {
            "username": "newuser", 
            "email": "newuser@gmail.com",  
            "password": "newpassword123",
        }
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)

    def test_user_login(self):
        """İstifadəçi loginini test edir."""
        data = {
            "username": self.test_username,
            "email": self.test_email,
            "password": self.test_password,
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)

    def test_user_profile(self):
        """Profil məlumatlarını əldə etməyi test edir."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.test_email)

    def test_google_login(self):
        """Google ilə giriş test edilir."""
        fake_google_token = "fake-token"
        google_api_url = "https://www.googleapis.com/oauth2/v3/tokeninfo"

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 400  # Google API cavabı saxta token üçün
            mock_get.return_value.json.return_value = {"error": "Invalid Google token"}

            response = self.client.post(self.google_login_url, {"token": fake_google_token})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)

