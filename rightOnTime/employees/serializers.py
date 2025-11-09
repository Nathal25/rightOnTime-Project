from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.
    Handles conversion between Employee objects and JSON format.
    Includes all model fields automatically.
    """
    class Meta:
        model = Employee  # The Django model to serialize
        fields = '__all__'  # Include all fields from the Employee model