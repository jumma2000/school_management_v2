from django.db import models
from decimal import Decimal
from django.utils import timezone

# ==========================================
# 1. الصفوف والشُعب والمواد
# ==========================================
class Grade(models.Model):
    name = models.CharField(max_length=50, verbose_name="الصف الدراسي", unique=True)
    
    class Meta:
        verbose_name = "الصف"
        verbose_name_plural = "الصفوف"
        
    def __str__(self):
        return self.name

class SchoolClass(models.Model):
    """الشُعب (مثلاً: السابع أ، السابع ب)"""
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='classes', verbose_name="الصف")
    section = models.CharField(max_length=10, verbose_name="الشعبة", help_text="مثال: أ، ب، ج")
    
    class Meta:
        unique_together = ('grade', 'section')
        verbose_name = "شعبة"
        verbose_name_plural = "الشُعب"
        
    def __str__(self):
        return f"{self.grade.name} - {self.section}"

class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم المادة")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='subjects', verbose_name="الصف")
    
    class Meta:
        verbose_name = "المادة"
        verbose_name_plural = "المواد"
        
    def __str__(self):
        return f"{self.name} - {self.grade.name}"

# ==========================================
# 2. المعلمين (مع البيانات المصرفية)
# ==========================================
class Teacher(models.Model):
    name = models.CharField(max_length=150, verbose_name="اسم المعلم")
    subject = models.CharField(max_length=100, verbose_name="التخصص/المادة")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف", blank=True, null=True)
    
    # البيانات المصرفية
    bank_name = models.CharField(max_length=100, verbose_name="اسم المصرف", blank=True, null=True)
    bank_branch = models.CharField(max_length=100, verbose_name="الفرع", blank=True, null=True)
    account_number = models.CharField(max_length=50, verbose_name="رقم الحساب", blank=True, null=True)
    bank_account = models.CharField(max_length=50, verbose_name="رقم الآيبان (IBAN)", blank=True, null=True)
    account_holder = models.CharField(max_length=150, verbose_name="اسم صاحب الحساب (الرباعي)", blank=True, null=True)
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التعيين", null=True, blank=True)

    class Meta:
        verbose_name = "معلم"
        verbose_name_plural = "المعلمين"

    def __str__(self):
        return f"{self.name} - {self.subject or 'عام'}"

# ==========================================
# 3. سجل حضور المعلمين
# ==========================================
class TeacherAttendance(models.Model):
    STATUS_CHOICES = [
        ('حاضر', 'حاضر'),
        ('غائب', 'غائب'),
        ('متأخر', 'متأخر'),
    ]
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendances', verbose_name="المعلم")
    date = models.DateField(default=timezone.now, verbose_name="التاريخ")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="الحالة")
    note = models.CharField(max_length=200, blank=True, null=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "سجل حضور معلم"
        verbose_name_plural = "سجلات حضور المعلمين"
        ordering = ['-date']

    def __str__(self):
        return f"{self.teacher.name} - {self.date} - {self.status}"

# ==========================================
# 4. جدول الحصص الأسبوعي (الجديد)
# ==========================================
class WeeklySchedule(models.Model):
    DAY_CHOICES = [
        ('الأحد', 'الأحد'), ('الاثنين', 'الاثنين'), ('الثلاثاء', 'الثلاثاء'),
        ('الأربعاء', 'الأربعاء'), ('الخميس', 'الخميس'),('الجمعة', 'الجمعة'),('السبت', 'السبت'),
    ]
    PERIOD_CHOICES = [
        ('الأولى', 'الأولى'), ('الثانية', 'الثانية'), ('الثالثة', 'الثالثة'),
        ('الرابعة', 'الرابعة'), ('الخامسة', 'الخامسة'), ('السادسة', 'السادسة'),
        ('السابعة', 'السابعة'), ('الثامنة', 'الثامنة'),
    ]
    
    day = models.CharField(max_length=20, choices=DAY_CHOICES, verbose_name="اليوم")
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, verbose_name="الحصة")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, verbose_name="الشعبة")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="المادة")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="المعلم")

    class Meta:
        unique_together = ('day', 'period', 'school_class')
        verbose_name = "حصة في الجدول"
        verbose_name_plural = "الجدول الأسبوعي"

    def __str__(self):
        return f"{self.day} - {self.period} - {self.school_class} ({self.teacher.name})"

# ==========================================
# 5. جدول تسعير الحصص
# ==========================================
class ClassPricing(models.Model):
    STAGE_CHOICES = [
        ('ابتدائي', 'ابتدائي'),
        ('إعدادي', 'إعدادي'),
        ('ثانوي', 'ثانوي'),
    ]
    
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, verbose_name="المرحلة")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="الصف")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="المادة")
    price_per_class = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الحصة (د.ل)")

    class Meta:
        unique_together = ('stage', 'grade', 'subject')
        verbose_name = "تسعير حصة"
        verbose_name_plural = "جدول أسعار الحصص"

    def __str__(self):
        return f"{self.stage} - {self.grade.name} - {self.subject.name}: {self.price_per_class} د.ل"

# ==========================================
# 6. نظام الرواتب
# ==========================================
class TeacherSalary(models.Model):
    MONTH_CHOICES = [
        ('يناير', 'يناير'), ('فبراير', 'فبراير'), ('مارس', 'مارس'),
        ('أبريل', 'أبريل'), ('مايو', 'مايو'), ('يونيو', 'يونيو'),
        ('يوليو', 'يوليو'), ('أغسطس', 'أغسطس'), ('سبتمبر', 'سبتمبر'),
        ('أكتوبر', 'أكتوبر'), ('نوفمبر', 'نوفمبر'), ('ديسمبر', 'ديسمبر'),
    ]
    YEAR_CHOICES = [(str(year), str(year)) for year in range(2020, 2031)]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='salaries', verbose_name="المعلم")
    month = models.CharField(max_length=20, choices=MONTH_CHOICES, verbose_name="الشهر")
    year = models.CharField(max_length=4, choices=YEAR_CHOICES, default='2026', verbose_name="السنة")
    
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="مكافآت")
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="خصومات")
    note = models.CharField(max_length=250, blank=True, null=True, verbose_name="ملاحظات")
    paid_date = models.DateField(auto_now_add=True, verbose_name="تاريخ الصرف")

    class Meta:
        verbose_name = "راتب شهري"
        verbose_name_plural = "رواتب المعلمين"
        ordering = ['-year', '-paid_date']

    def __str__(self):
        return f"راتب {self.teacher.name} لشهر {self.month} {self.year}"

    @property
    def total_classes_amount(self):
        try:
            return sum((item.total_amount for item in self.salary_items.all()), Decimal('0.00'))
        except Exception:
            return Decimal('0.00')

    @property
    def net_salary(self):
        try:
            return (self.total_classes_amount + self.bonus) - self.deductions
        except Exception:
            return Decimal('0.00')

# ==========================================
# 7. بنود الراتب (تفاصيل الحصص)
# ==========================================
class SalaryItem(models.Model):
    salary = models.ForeignKey(TeacherSalary, on_delete=models.CASCADE, related_name='salary_items', verbose_name="سجل الراتب")
    pricing = models.ForeignKey(ClassPricing, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="التسعير (الصف والمادة)")
    total_classes = models.PositiveIntegerField(default=0, verbose_name="عدد الحصص")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الحصة (د.ل)")

    @property
    def total_amount(self):
        try:
            return Decimal(self.total_classes) * self.hourly_rate
        except Exception:
            return Decimal('0.00')

    def __str__(self):
        return f"{self.total_classes} حصة × {self.hourly_rate} د.ل"
    