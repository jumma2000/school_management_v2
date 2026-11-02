from django.contrib import admin
from .models import (
    Grade, SchoolClass, Subject, Teacher, TeacherAttendance, 
    ClassPricing, TeacherSalary, SalaryItem, WeeklySchedule
)

# --- إدارة الصفوف والشُعب والمواد ---
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'grade', 'section')
    list_filter = ('grade',)
    search_fields = ('grade__name', 'section')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'grade')
    list_filter = ('grade',)
    search_fields = ('name',)

# --- إدارة المعلمين (مع الحضور) ---
class TeacherAttendanceInline(admin.TabularInline):
    model = TeacherAttendance
    extra = 1
    verbose_name = "سجل حضور"
    verbose_name_plural = "سجلات الحضور"

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'phone', 'bank_name', 'is_active')
    list_filter = ('is_active', 'subject', 'bank_name')
    search_fields = ('name', 'phone', 'bank_account')
    inlines = [TeacherAttendanceInline]

@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'status', 'note')
    list_filter = ('status', 'date', 'teacher')
    search_fields = ('teacher__name',)

# --- إدارة التسعير والرواتب ---
@admin.register(ClassPricing)
class ClassPricingAdmin(admin.ModelAdmin):
    list_display = ('id', 'stage', 'grade', 'subject', 'price_per_class')
    list_filter = ('stage', 'grade')
    search_fields = ('grade__name', 'subject__name')

class SalaryItemInline(admin.TabularInline):
    model = SalaryItem
    extra = 1
    verbose_name = "بند حصص"
    verbose_name_plural = "بنود الحصص"

@admin.register(TeacherSalary)
class TeacherSalaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher', 'month', 'year', 'net_salary', 'paid_date')
    list_filter = ('year', 'month', 'teacher')
    search_fields = ('teacher__name',)
    inlines = [SalaryItemInline]

# --- إدارة الجدول الأسبوعي ---
@admin.register(WeeklySchedule)
class WeeklyScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'period', 'school_class', 'subject', 'teacher')
    list_filter = ('day', 'period', 'school_class__grade', 'teacher')
    search_fields = ('teacher__name', 'subject__name')
    