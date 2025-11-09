from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeViewSet(ModelViewSet):
    """
    ViewSet for Employee CRUD operations.
    Provides list, create, retrieve, update, and delete actions.
    Only accessible to authenticated users.
    """
    queryset = Employee.objects.all()  # All Employee records from database
    serializer_class = EmployeeSerializer  # Serializer to convert Employee <-> JSON
    permission_classes = [IsAuthenticated]  # Requires valid JWT token to access