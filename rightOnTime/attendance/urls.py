from django.urls import path
from .views import check_in, check_out, list_all_attendance

urlpatterns = [
    path('checkin/', check_in),
    path('checkout/', check_out),
    path('all/', list_all_attendance),
]
