from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import AdminLoginSerializer

# Create your views here.
class AdminLoginView(TokenObtainPairView):
    """
    Admin-only login endpoint that generates JWT tokens.
    Uses AdminLoginSerializer to restrict access to staff users only.
    """
    serializer_class = AdminLoginSerializer  # Custom serializer with is_staff validation.