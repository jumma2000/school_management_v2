from django.contrib import admin
from django.urls import path, include
from academics.api import GradeListAPI
from academics.api import GradeListAPI, TeacherListAPI
from students.api import (
    StudentListAPI, 
    StudentDeleteAPI, 
    PaymentCreateAPI, 
    StudentUpdateAPI
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('academics.urls')),
    path('students/', include('students.urls')),
    
    # واجهات API
    path('api/students/', StudentListAPI.as_view(), name='api_students'),
    path('api/students/<int:pk>/', StudentDeleteAPI.as_view(), name='api_student_delete'),
    path('api/students/<int:pk>/update/', StudentUpdateAPI.as_view(), name='api_student_update'),
    path('api/payments/', PaymentCreateAPI.as_view(), name='api_payments'),
    path('api/grades/', GradeListAPI.as_view(), name='api_grades'),
    path('api/teachers/', TeacherListAPI.as_view(), name='api_teachers'),

]