from django.contrib import admin
from .models import Student, Payment, StudentAttendance

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    verbose_name = "دفعة"
    verbose_name_plural = "الدفعات"

class AttendanceInline(admin.TabularInline):
    model = StudentAttendance
    extra = 1
    verbose_name = "حضور"
    verbose_name_plural = "سجل الحضور"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'phone', 'net_fees', 'total_paid', 'balance', 'is_active')
    list_filter = ('grade', 'is_active')
    search_fields = ('name', 'phone', 'parent_name', 'bank_account', 'account_number')
    inlines = [PaymentInline, AttendanceInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'date', 'note')
    list_filter = ('date',)
    search_fields = ('student__name',)

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'note')
    list_filter = ('status', 'date', 'student__grade')
    search_fields = ('student__name',)
    