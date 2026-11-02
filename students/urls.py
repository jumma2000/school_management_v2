from django.urls import path
from .views import (
    StudentListView, StudentCreateView, PaymentCreateView, 
    StudentUpdateView, StudentDeleteView, StudentAttendanceView
)

urlpatterns = [
    path('', StudentListView.as_view(), name='student_list'),
    path('add/', StudentCreateView.as_view(), name='student_add'),
    path('<int:student_id>/pay/', PaymentCreateView.as_view(), name='payment_add'),
    path('<int:pk>/edit/', StudentUpdateView.as_view(), name='student_update'),
    path('<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    path('attendance/', StudentAttendanceView.as_view(), name='student_attendance'), # <--- جديد
]
