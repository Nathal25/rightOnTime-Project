from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime
from .models import Attendance
from employees.models import Employee


@api_view(['POST'])
@permission_classes([AllowAny])
def check_in(request):
    document_id = request.data.get('document_id')

    if not document_id:
        return Response({"error": "document_id requerido"}, status=400)

    try:
        employee = Employee.objects.get(document_id=document_id)
    except Employee.DoesNotExist:
        return Response({"error": "Empleado no existe"}, status=404)

    today = datetime.now().date()

    if Attendance.objects.filter(employee=employee, date=today).exists():
        return Response({"error": "Este empleado ya tiene asistencia hoy"}, status=409)

    Attendance.objects.create(
        id_attendance=f"A-{datetime.now().timestamp()}",
        employee=employee,
        check_in_time=datetime.now().time()
    )

    return Response({"message": "Entrada registrada correctamente"})


@api_view(['POST'])
@permission_classes([AllowAny])
def check_out(request):
    document_id = request.data.get('document_id')

    if not document_id:
        return Response({"error": "document_id requerido"}, status=400)

    try:
        employee = Employee.objects.get(document_id=document_id)
    except Employee.DoesNotExist:
        return Response({"error": "Empleado no existe"}, status=404)

    today = datetime.now().date()

    attendance = Attendance.objects.filter(employee=employee, date=today).first()

    if not attendance:
        return Response({"error": "No hay check-in registrado hoy"}, status=409)

    if attendance.check_out_time is not None:
        return Response({"error": "Ya has registrado salida hoy"}, status=409)

    attendance.check_out_time = datetime.now().time()
    attendance.save()

    return Response({"message": "Salida registrada correctamente"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_attendance(request):
    data = Attendance.objects.all().values()
    return Response(data)
