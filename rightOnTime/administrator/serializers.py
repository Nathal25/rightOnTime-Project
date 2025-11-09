from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class AdminLoginSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that only allows staff users to login.
    Extends TokenObtainPairSerializer to add admin-only validation.
    """
    
    def validate(self, attrs):
        # Validate credentials and generate JWT tokens
        data = super().validate(attrs)
        
        # Check if user is staff/admin
        if not self.user.is_staff:
            raise Exception("Only administrators can login")
        
        # Return tokens if user is staff
        return data