from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers as rest_serializers
from .serializers import AdminLoginSerializer

User = get_user_model()


class AdminLoginSerializerTest(TestCase):
    """Test cases for AdminLoginSerializer"""
    
    def setUp(self):
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username="admin_user",
            email="admin@test.com",
            password="adminpass123",
            id_administrator="ADMIN001",
            phone_number=3001234567
        )
        self.staff_user.is_staff = True
        self.staff_user.save()
        
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username="regular_user",
            email="user@test.com",
            password="userpass123",
            id_administrator="USER001",
            phone_number=3001234568
        )
    
    def test_admin_login_success(self):
        """Test successful admin login with staff user"""
        serializer = AdminLoginSerializer(data={
            'username': 'admin_user',
            'password': 'adminpass123'
        })
        self.assertTrue(serializer.is_valid())
        validated_data = serializer.validated_data
        self.assertIn('access', validated_data)
        self.assertIn('refresh', validated_data)
    
    def test_admin_login_non_staff_user(self):
        """Test that non-staff users cannot login"""
        serializer = AdminLoginSerializer(data={
            'username': 'regular_user',
            'password': 'userpass123'
        })
        
        with self.assertRaises(rest_serializers.ValidationError) as context:
            serializer.is_valid(raise_exception=True)
            serializer.validated_data
        
        self.assertIn('detail', str(context.exception))
    
    def test_admin_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        serializer = AdminLoginSerializer(data={
            'username': 'admin_user',
            'password': 'wrongpassword'
        })
        # Should raise validation error for invalid credentials
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)
