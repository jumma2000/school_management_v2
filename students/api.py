from rest_framework import serializers, generics, status
from rest_framework.response import Response
from .models import Student, Payment

# ==========================================
# 1. تحويل بيانات الطالب إلى JSON
# ==========================================
class StudentSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'name', 'parent_name', 'phone', 'grade', 'grade_name', 'total_fees', 'balance', 'is_active']

# ==========================================
# 2. واجهة جلب وإضافة الطلاب
# ==========================================
class StudentListAPI(generics.ListCreateAPIView):
    queryset = Student.objects.filter(is_active=True).order_by('-id')
    serializer_class = StudentSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": f"حدث خطأ أثناء إضافة الطالب: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# ==========================================
# 3. واجهة حذف طالب
# ==========================================
class StudentDeleteAPI(generics.DestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": f"حدث خطأ أثناء حذف الطالب: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# ==========================================
# 4. تحويل بيانات الدفعة إلى JSON
# ==========================================
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'student', 'amount', 'note']

# ==========================================
# 5. واجهة تسجيل الدفعات
# ==========================================
class PaymentCreateAPI(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": f"حدث خطأ أثناء تسجيل الدفعة: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
class StudentUpdateAPI(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    