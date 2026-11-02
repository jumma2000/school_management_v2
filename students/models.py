from django.db import models
from academics.models import Grade
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone

class Student(models.Model):
    name = models.CharField(max_length=150, verbose_name="اسم الطالب الرباعي")
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, verbose_name="الصف الدراسي")
    parent_name = models.CharField(max_length=150, verbose_name="اسم ولي الأمر", blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="رقم الواتساب", blank=True, null=True, help_text="مثال: 218910000000")
    
    # --- البيانات المصرفية لولي الأمر ---
    bank_name = models.CharField(max_length=100, verbose_name="اسم المصرف", blank=True, null=True)
    bank_branch = models.CharField(max_length=100, verbose_name="الفرع", blank=True, null=True)
    bank_account = models.CharField(max_length=50, verbose_name="رقم الحساب (IBAN)", blank=True, null=True)
    account_number = models.CharField(max_length=50, verbose_name="رقم الحساب", blank=True, null=True)
    account_holder = models.CharField(max_length=150, verbose_name="اسم صاحب الحساب (الرباعي)", blank=True, null=True)

    # بيانات مالية
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="إجمالي الرسوم")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="التخفيضات")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")

    @property
    def net_fees(self):
        try:
            return self.total_fees - self.discount
        except Exception:
            return Decimal('0.00')

    @property
    def total_paid(self):
        try:
            paid = self.payments.aggregate(total=Sum('amount'))['total']
            return paid if paid is not None else Decimal('0.00')
        except Exception:
            return Decimal('0.00')

    @property
    def balance(self):
        try:
            return self.net_fees - self.total_paid
        except Exception:
            return Decimal('0.00')

    class Meta:
        verbose_name = "طالب"
        verbose_name_plural = "الطلاب"

    def __str__(self):
        return self.name

class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments', verbose_name="الطالب")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ المدفوع")
    date = models.DateField(auto_now_add=True, verbose_name="تاريخ الدفع")
    note = models.CharField(max_length=200, blank=True, null=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "دفعة"
        verbose_name_plural = "الدفعات"

    def __str__(self):
        return f"{self.student.name} - {self.amount}"

# ==========================================
# سجل حضور الطلاب (الغياب)
# ==========================================
class StudentAttendance(models.Model):
    STATUS_CHOICES = [
        ('حاضر', 'حاضر'),
        ('غائب', 'غائب'),
        ('متأخر', 'متأخر'),
        ('بعذر', 'بعذر'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances', verbose_name="الطالب")
    date = models.DateField(default=timezone.now, verbose_name="التاريخ")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="الحالة")
    note = models.CharField(max_length=200, blank=True, null=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "سجل حضور طالب"
        verbose_name_plural = "سجلات حضور الطلاب"
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"