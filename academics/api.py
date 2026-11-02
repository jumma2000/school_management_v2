from rest_framework import generics, serializers
from .models import Grade

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name']

class GradeListAPI(generics.ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

from rest_framework import serializers, generics
from .models import Teacher

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'subject', 'phone', 'is_active']

class TeacherListAPI(generics.ListCreateAPIView):
    queryset = Teacher.objects.filter(is_active=True).order_by('-id')
    serializer_class = TeacherSerializer
        