from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Q
from decimal import Decimal
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.core.paginator import Paginator

# استدعاء النماذج
from students.models import Student, Payment
from .models import (
    Grade, Subject, Teacher, TeacherAttendance, 
    ClassPricing, TeacherSalary, SalaryItem,
    SchoolClass, WeeklySchedule
)

import shutil
from datetime import datetime
from django.conf import settings

# ==========================================
# 0. النسخ الاحتياطي
# ==========================================
from django.http import FileResponse
import os

class BackupDatabaseView(View):
    def get(self, request):
        try:
            db_path = settings.BASE_DIR / 'db.sqlite3'
            
            if not db_path.exists():
                messages.error(request, "ملف قاعدة البيانات غير موجود!")
                return redirect('home')
                
            # تحميل الملف مباشرة للمتصفح
            response = FileResponse(open(db_path, 'rb'), as_attachment=True, filename=f"school_backup_{timezone.now().strftime('%Y%m%d')}.sqlite3")
            return response
            
        except Exception as e:
            messages.error(request, f"فشل في تحميل النسخة الاحتياطية: {str(e)}")
            return redirect('home')

# ==========================================
# 1. لوحة التحكم
# ==========================================
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            today = timezone.now().date()
            
            # قاموس لتحويل رقم الشهر إلى اسمه العربي لمطابقة قاعدة البيانات
            months_ar = {
                1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
                5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
                9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
            }
            current_month_name = months_ar.get(today.month)
            current_year = str(today.year)

            # 1. إحصائيات أساسية
            total_students = Student.objects.filter(is_active=True).count()
            total_teachers = Teacher.objects.filter(is_active=True).count()

            # 2. الإحصائيات المالية للطلاب
            total_paid = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            students = Student.objects.filter(is_active=True)
            total_expected = sum((s.net_fees for s in students), Decimal('0.00'))
            total_debts = total_expected - total_paid
            today_paid = Payment.objects.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            # 3. رواتب الشهر الحالي (حساب يدوي لأن net_salary هو property وليس حقل DB)
            month_salaries_qs = TeacherSalary.objects.filter(
                month=current_month_name,
                year=current_year
            )
            month_salaries = sum((s.net_salary for s in month_salaries_qs), Decimal('0.00'))

            # 4. الجدول والحضور اليومي
            day_name_ar = {
                0: 'الاثنين', 1: 'الثلاثاء', 2: 'الأربعاء',
                3: 'الخميس', 4: 'الجمعة', 5: 'السبت', 6: 'الأحد'
            }.get(today.weekday(), 'الأحد')

            today_classes_count = WeeklySchedule.objects.filter(day=day_name_ar).count()
            today_absences = TeacherAttendance.objects.filter(date=today, status='غائب').count()

            # 5. أحدث الدفعات
            recent_payments = Payment.objects.all().order_by('-date')[:5]

            context.update({
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_paid': total_paid,
                'total_debts': total_debts,
                'today_paid': today_paid,
                'month_salaries': month_salaries,
                'today_classes_count': today_classes_count,
                'today_absences': today_absences,
                'recent_payments': recent_payments,
                'today': today,
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ أثناء تحميل الإحصائيات: {str(e)}")
            context.update({
                'total_students': 0, 'total_teachers': 0, 'total_paid': 0, 'total_debts': 0, 
                'today_paid': 0, 'month_salaries': 0, 'today_classes_count': 0, 
                'today_absences': 0, 'recent_payments': []
            })
        return context
    
        context = super().get_context_data(**kwargs)
        try:
            today = timezone.now().date()
            current_month = today.month
            current_year = today.year

            # 1. إحصائيات أساسية
            total_students = Student.objects.filter(is_active=True).count()
            total_teachers = Teacher.objects.filter(is_active=True).count()

            # 2. الإحصائيات المالية
            total_paid = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            students = Student.objects.filter(is_active=True)
            total_expected = sum((s.net_fees for s in students), Decimal('0.00'))
            total_debts = total_expected - total_paid
            today_paid = Payment.objects.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            # إجمالي الرواتب المصروفة هذا الشهر
            month_salaries = TeacherSalary.objects.filter(
                month__icontains=str(current_month), # ملاحظة: يعتمد على طريقة تخزين الشهر (نص أو رقم)
                year=str(current_year)
            ).aggregate(Sum('net_salary'))['net_salary__sum'] or Decimal('0.00')

            # 3. الجدول والحضور اليومي
            day_name_ar = {
                0: 'الاثنين', 1: 'الثلاثاء', 2: 'الأربعاء',
                3: 'الخميس', 4: 'الجمعة', 5: 'السبت', 6: 'الأحد'
            }.get(today.weekday(), 'الأحد')

            # عدد حصص اليوم
            today_classes_count = WeeklySchedule.objects.filter(day=day_name_ar).count()
            
            # عدد غياب المعلمين اليوم
            today_absences = TeacherAttendance.objects.filter(date=today, status='غائب').count()

            # 4. أحدث الدفعات
            recent_payments = Payment.objects.all().order_by('-date')[:5]

            context.update({
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_paid': total_paid,
                'total_debts': total_debts,
                'today_paid': today_paid,
                'month_salaries': month_salaries,
                'today_classes_count': today_classes_count,
                'today_absences': today_absences,
                'recent_payments': recent_payments,
                'today': today,
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ أثناء تحميل الإحصائيات: {str(e)}")
            # قيم افتراضية في حال حدوث خطأ
            context.update({
                'total_students': 0, 'total_teachers': 0, 'total_paid': 0, 'total_debts': 0, 
                'today_paid': 0, 'month_salaries': 0, 'today_classes_count': 0, 
                'today_absences': 0, 'recent_payments': []
            })
        return context
# ==========================================
# 2. إدارة الصفوف
# ==========================================
class GradeListView(TemplateView):
    template_name = 'academics/grade_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['grades'] = Grade.objects.all().order_by('id')
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context['grades'] = []
        return context

class GradeCreateView(View):
    def get(self, request):
        return render(request, 'academics/grade_form.html')

    def post(self, request):
        try:
            name = request.POST.get('name')
            if name:
                if Grade.objects.filter(name=name).exists():
                    messages.warning(request, "هذا الصف موجود بالفعل.")
                else:
                    Grade.objects.create(name=name)
                    messages.success(request, "تمت إضافة الصف بنجاح!")
                    return redirect('grade_list')
            else:
                messages.error(request, "الرجاء إدخال اسم الصف.")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء الإضافة: {str(e)}")
        return render(request, 'academics/grade_form.html')

class GradeUpdateView(UpdateView):
    model = Grade
    template_name = 'academics/grade_form.html'
    fields = ['name']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context

    def form_valid(self, form):
        try:
            messages.success(self.request, "تم تعديل الصف بنجاح!")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"حدث خطأ أثناء التعديل: {str(e)}")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('grade_list')

class GradeDeleteView(DeleteView):
    model = Grade
    template_name = 'academics/grade_confirm_delete.html'
    success_url = reverse_lazy('grade_list')

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(request, "تم حذف الصف بنجاح!")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء الحذف: {str(e)}")
            return redirect('grade_list')

# ==========================================
# 3. التقارير
# ==========================================
class DebtReportView(TemplateView):
    template_name = 'academics/debt_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            students_with_debts = [s for s in Student.objects.filter(is_active=True) if s.balance > 0]
            total_debts = sum((s.balance for s in students_with_debts), Decimal('0.00'))
            
            context.update({
                'students': students_with_debts,
                'total_debts': total_debts,
                'today': timezone.now(),
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context.update({'students': [], 'total_debts': Decimal('0.00'), 'today': timezone.now()})
        return context

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os

class DebtReportPDFView(TemplateView):
    template_name = 'academics/debt_report_pdf.html'

    def get(self, request, *args, **kwargs):
        try:
            students_with_debts = [s for s in Student.objects.filter(is_active=True) if s.balance > 0]
            total_debts = sum((s.balance for s in students_with_debts), Decimal('0.00'))
            
            context = {
                'students': students_with_debts,
                'total_debts': total_debts,
                'today': timezone.now(),
            }
            
            template = get_template(self.template_name)
            html = template.render(context)
            
            # --- التعديل الجديد: تحديد مسار الخط العربي ---
            font_path = os.path.join(settings.BASE_DIR, 'static', 'Cairo-Regular.ttf')
            
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="debt_report.pdf"'
            
            # --- التعديل الجديد: إخبار المكتبة باستخدام الخط ---
            pisa_status = pisa.CreatePDF(
                html, 
                dest=response,
                link_callback=lambda uri, rel: os.path.join(settings.BASE_DIR, uri) # للتأكد من قراءة الملفات
            )
            
            if pisa_status.err:
                return HttpResponse('حدث خطأ أثناء إنشاء ملف PDF', status=500)
            return response
        except Exception as e:
            return HttpResponse(f'حدث خطأ: {str(e)}', status=500)
        
class StudentDataReportView(TemplateView):
    template_name = 'academics/student_data_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            students = Student.objects.filter(is_active=True).order_by('grade__name', 'name')
            context.update({
                'students': students,
                'today': timezone.now(),
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context.update({'students': [], 'today': timezone.now()})
        return context

class TeacherDataReportView(TemplateView):
    template_name = 'academics/teacher_data_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            teachers = Teacher.objects.filter(is_active=True).order_by('name')
            context.update({
                'teachers': teachers,
                'today': timezone.now(),
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context.update({'teachers': [], 'today': timezone.now()})
        return context

# ==========================================
# 4. إدارة المعلمين
# ==========================================
class TeacherListView(TemplateView):
    template_name = 'academics/teacher_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            teachers_list = Teacher.objects.filter(is_active=True).order_by('-id')
            search_query = self.request.GET.get('q', '').strip()
            if search_query:
                teachers_list = teachers_list.filter(
                    Q(name__icontains=search_query) | 
                    Q(phone__icontains=search_query) |
                    Q(subject__icontains=search_query)
                )
            
            paginator = Paginator(teachers_list, 10) 
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context['teachers'] = page_obj
            context['page_obj'] = page_obj
            context['search_query'] = search_query
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context['teachers'] = []
        return context

class TeacherCreateView(View):
    def get(self, request):
        return render(request, 'academics/teacher_form.html')

    def post(self, request):
        try:
            name = request.POST.get('name')
            subject = request.POST.get('subject')
            phone = request.POST.get('phone', '')
            
            bank_name = request.POST.get('bank_name', '')
            bank_branch = request.POST.get('bank_branch', '')
            account_number = request.POST.get('account_number', '')
            bank_account = request.POST.get('bank_account', '')
            account_holder = request.POST.get('account_holder', '')
            
            if not name or not subject:
                messages.warning(request, "الرجاء إدخال الاسم والتخصص.")
                return redirect('teacher_add')
                
            Teacher.objects.create(
                name=name, subject=subject, phone=phone,
                bank_name=bank_name, bank_branch=bank_branch,
                account_number=account_number, bank_account=bank_account,
                account_holder=account_holder
            )
            messages.success(request, "تمت إضافة المعلم بنجاح!")
            return redirect('teacher_list')
        except Exception as e:
            messages.error(request, f"فشل في الإضافة: {str(e)}")
            return redirect('teacher_add')

class TeacherUpdateView(View):
    def get(self, request, pk):
        try:
            teacher = Teacher.objects.get(id=pk)
            return render(request, 'academics/teacher_form.html', {'object': teacher, 'is_update': True})
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            return redirect('teacher_list')

    def post(self, request, pk):
        try:
            teacher = Teacher.objects.get(id=pk)
            teacher.name = request.POST.get('name')
            teacher.subject = request.POST.get('subject')
            teacher.phone = request.POST.get('phone', '')
            
            teacher.bank_name = request.POST.get('bank_name', teacher.bank_name)
            teacher.bank_branch = request.POST.get('bank_branch', teacher.bank_branch)
            teacher.account_number = request.POST.get('account_number', teacher.account_number)
            teacher.bank_account = request.POST.get('bank_account', teacher.bank_account)
            teacher.account_holder = request.POST.get('account_holder', teacher.account_holder)
            
            teacher.save()
            messages.success(self.request, "تم تعديل بيانات المعلم بنجاح!")
            return redirect('teacher_list')
        except Exception as e:
            messages.error(self.request, f"فشل في التعديل: {str(e)}")
            return redirect('teacher_update', pk=pk)

class TeacherDeleteView(DeleteView):
    model = Teacher
    template_name = 'academics/teacher_confirm_delete.html'
    success_url = reverse_lazy('teacher_list')

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(request, "تم حذف المعلم بنجاح!")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('teacher_list')

# ==========================================
# 5. سجل الدفعات
# ==========================================
class PaymentHistoryView(TemplateView):
    template_name = 'academics/payment_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            payments = Payment.objects.all().order_by('-date', '-id')
            search_query = self.request.GET.get('q', '').strip()
            if search_query:
                payments = payments.filter(
                    Q(student__name__icontains=search_query) | 
                    Q(note__icontains=search_query) |
                    Q(date__icontains=search_query)
                )
            
            total_amount = sum((p.amount for p in payments), Decimal('0.00'))

            paginator = Paginator(payments, 20) 
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context.update({
                'payments': page_obj,
                'page_obj': page_obj,
                'total_amount': total_amount,
                'search_query': search_query,
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context.update({'payments': [], 'total_amount': Decimal('0.00'), 'search_query': ''})
        return context

# ==========================================
# 6. إدارة تسعير الحصص
# ==========================================
class PricingListView(TemplateView):
    template_name = 'academics/pricing_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            pricings_list = ClassPricing.objects.all().order_by('stage', 'grade__name')
            
            paginator = Paginator(pricings_list, 15) 
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context['pricings'] = page_obj
            context['page_obj'] = page_obj
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context['pricings'] = []
        return context

class PricingCreateView(View):
    def get(self, request):
        try:
            grades = Grade.objects.all()
            subjects = Subject.objects.all()
            stages = ClassPricing.STAGE_CHOICES
            return render(request, 'academics/pricing_form.html', {
                'grades': grades, 'subjects': subjects, 'stages': stages
            })
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('pricing_list')

    def post(self, request):
        try:
            stage = request.POST.get('stage')
            grade_id = request.POST.get('grade')
            subject_id = request.POST.get('subject')
            price = Decimal(request.POST.get('price', '0'))

            if not stage or not grade_id or not subject_id:
                messages.warning(request, "الرجاء ملء جميع الحقول.")
                return redirect('pricing_add')

            grade = Grade.objects.get(id=grade_id)
            subject = Subject.objects.get(id=subject_id)

            if ClassPricing.objects.filter(stage=stage, grade=grade, subject=subject).exists():
                messages.warning(request, "هذا التسعير موجود بالفعل.")
            else:
                ClassPricing.objects.create(
                    stage=stage, grade=grade, subject=subject, price_per_class=price
                )
                messages.success(request, "تمت إضافة التسعير بنجاح!")
            return redirect('pricing_list')
        except Exception as e:
            messages.error(request, f"فشل في الإضافة: {str(e)}")
            return redirect('pricing_add')

class PricingUpdateView(View):
    def get(self, request, pk):
        try:
            pricing = ClassPricing.objects.get(id=pk)
            grades = Grade.objects.all()
            subjects = Subject.objects.all()
            stages = ClassPricing.STAGE_CHOICES
            return render(request, 'academics/pricing_form.html', {
                'object': pricing,
                'grades': grades, 
                'subjects': subjects, 
                'stages': stages,
                'is_update': True
            })
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('pricing_list')

    def post(self, request, pk):
        try:
            pricing = ClassPricing.objects.get(id=pk)
            stage = request.POST.get('stage')
            grade_id = request.POST.get('grade')
            subject_id = request.POST.get('subject')
            price = Decimal(request.POST.get('price', '0'))

            if not stage or not grade_id or not subject_id:
                messages.warning(request, "الرجاء ملء جميع الحقول.")
                return redirect('pricing_update', pk=pk)

            pricing.stage = stage
            pricing.grade = Grade.objects.get(id=grade_id)
            pricing.subject = Subject.objects.get(id=subject_id)
            pricing.price_per_class = price
            pricing.save()

            messages.success(request, "تم تعديل التسعير بنجاح!")
            return redirect('pricing_list')
        except Exception as e:
            messages.error(request, f"فشل في التعديل: {str(e)}")
            return redirect('pricing_update', pk=pk)

class PricingDeleteView(DeleteView):
    model = ClassPricing
    template_name = 'academics/pricing_confirm_delete.html'
    success_url = reverse_lazy('pricing_list')

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(request, "تم حذف التسعير بنجاح!")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('pricing_list')

# ==========================================
# 7. إدارة الرواتب (مع الحساب التلقائي)
# ==========================================
class SalaryCreateView(View):
    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            pricings = ClassPricing.objects.all()
            months = TeacherSalary.MONTH_CHOICES
            years = TeacherSalary.YEAR_CHOICES

            # الحساب التلقائي لعدد الحصص
            weekly_schedules = WeeklySchedule.objects.filter(teacher=teacher)
            total_weekly_classes = weekly_schedules.count()

            current_month = timezone.now().month
            current_year = timezone.now().year
            
            attendances = TeacherAttendance.objects.filter(
                teacher=teacher, 
                date__month=current_month, 
                date__year=current_year
            )
            absences = attendances.filter(status='غائب').count()

            estimated_total = total_weekly_classes * 4 
            final_classes = estimated_total - absences

            default_data = {
                'weekly_classes': total_weekly_classes,
                'absences': absences,
                'final_classes': final_classes if final_classes > 0 else 0,
            }

            return render(request, 'academics/salary_form.html', {
                'teacher': teacher,
                'pricings': pricings,
                'months': months,
                'years': years,
                'default_data': default_data,
            })
        except Teacher.DoesNotExist:
            messages.error(request, "المعلم غير موجود.")
            return redirect('teacher_list')
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('teacher_list')

    def post(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            month = request.POST.get('month')
            year = request.POST.get('year')
            bonus = Decimal(request.POST.get('bonus', '0') or '0')
            deductions = Decimal(request.POST.get('deductions', '0') or '0')
            note = request.POST.get('note', '')

            salary = TeacherSalary.objects.create(
                teacher=teacher, month=month, year=year,
                bonus=bonus, deductions=deductions, note=note
            )

            pricing_ids = request.POST.getlist('pricing_id[]')
            classes_list = request.POST.getlist('classes[]')

            for i in range(len(pricing_ids)):
                if pricing_ids[i] and classes_list[i]:
                    pricing = ClassPricing.objects.get(id=pricing_ids[i])
                    total_classes = int(classes_list[i])
                    
                    SalaryItem.objects.create(
                        salary=salary, pricing=pricing,
                        total_classes=total_classes, hourly_rate=pricing.price_per_class
                    )

            messages.success(request, f"تم احتساب راتب {teacher.name} لشهر {month} {year} بنجاح!")
            return redirect('salary_list')

        except Exception as e:
            messages.error(request, f"فشل في احتساب الراتب: {str(e)}")
            return redirect('teacher_list')

class SalaryListView(TemplateView):
    template_name = 'academics/salary_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            salaries_list = TeacherSalary.objects.all().order_by('-paid_date')
            
            search_query = self.request.GET.get('q', '').strip()
            if search_query:
                salaries_list = salaries_list.filter(
                    Q(teacher__name__icontains=search_query) | 
                    Q(month__icontains=search_query) |
                    Q(year__icontains=search_query)
                )
            
            paginator = Paginator(salaries_list, 15) 
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context['salaries'] = page_obj
            context['page_obj'] = page_obj
            context['search_query'] = search_query
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context['salaries'] = []
        return context

# ==========================================
# 8. إدارة المواد
# ==========================================
class SubjectListView(TemplateView):
    template_name = 'academics/subject_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            subjects = Subject.objects.all().order_by('grade__name', 'name')
            context['subjects'] = subjects
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context['subjects'] = []
        return context

class SubjectCreateView(View):
    def get(self, request):
        try:
            grades = Grade.objects.all()
            return render(request, 'academics/subject_form.html', {'grades': grades})
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('subject_list')

    def post(self, request):
        try:
            name = request.POST.get('name')
            grade_id = request.POST.get('grade')
            
            if not name or not grade_id:
                messages.warning(request, "الرجاء إدخال اسم المادة واختيار الصف.")
                return redirect('subject_add')

            grade = Grade.objects.get(id=grade_id)
            Subject.objects.create(name=name, grade=grade)
            messages.success(request, "تمت إضافة المادة بنجاح!")
            return redirect('subject_list')
        except Exception as e:
            messages.error(request, f"فشل في الإضافة: {str(e)}")
            return redirect('subject_add')

class SubjectUpdateView(View):
    def get(self, request, pk):
        try:
            subject = Subject.objects.get(id=pk)
            grades = Grade.objects.all()
            return render(request, 'academics/subject_form.html', {
                'object': subject, 'grades': grades, 'is_update': True
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            return redirect('subject_list')

    def post(self, request, pk):
        try:
            subject = Subject.objects.get(id=pk)
            subject.name = request.POST.get('name')
            subject.grade = Grade.objects.get(id=request.POST.get('grade'))
            subject.save()
            messages.success(self.request, "تم تعديل المادة بنجاح!")
            return redirect('subject_list')
        except Exception as e:
            messages.error(self.request, f"فشل في التعديل: {str(e)}")
            return redirect('subject_update', pk=pk)

class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = 'academics/subject_confirm_delete.html'
    success_url = reverse_lazy('subject_list')

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(request, "تم حذف المادة بنجاح!")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('subject_list')

# ==========================================
# 9. سجل حضور المعلمين
# ==========================================
class TeacherAttendanceView(TemplateView):
    template_name = 'academics/teacher_attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            teachers = Teacher.objects.filter(is_active=True).order_by('name')
            today = timezone.now().date()
            attendance_today = {a.teacher_id: a for a in TeacherAttendance.objects.filter(date=today)}
            
            teachers_with_status = []
            for teacher in teachers:
                attendance = attendance_today.get(teacher.id)
                teachers_with_status.append({
                    'teacher': teacher,
                    'status': attendance.status if attendance else 'حاضر',
                    'note': attendance.note if attendance else ''
                })

            context.update({
                'teachers_with_status': teachers_with_status,
                'today': today,
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context.update({'teachers_with_status': [], 'today': timezone.now()})
        return context

    def post(self, request):
        try:
            today = timezone.now().date()
            teacher_ids = request.POST.getlist('teacher_id[]')
            statuses = request.POST.getlist('status[]')
            notes = request.POST.getlist('note[]')

            for i in range(len(teacher_ids)):
                if teacher_ids[i] and statuses[i]:
                    teacher = Teacher.objects.get(id=teacher_ids[i])
                    TeacherAttendance.objects.update_or_create(
                        teacher=teacher, date=today,
                        defaults={'status': statuses[i], 'note': notes[i]}
                    )
            messages.success(request, "تم حفظ سجل الحضور بنجاح!")
            return redirect('teacher_attendance')
        except Exception as e:
            messages.error(request, f"فشل في حفظ الحضور: {str(e)}")
            return redirect('teacher_attendance')

# ==========================================
# 10. تقارير الحضور
# ==========================================
class StudentAttendanceReportView(TemplateView):
    template_name = 'academics/student_attendance_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from students.models import StudentAttendance
            attendances = StudentAttendance.objects.all().order_by('-date', 'student__name')
            search_query = self.request.GET.get('q', '').strip()
            if search_query:
                attendances = attendances.filter(student__name__icontains=search_query)

            context.update({
                'attendances': attendances,
                'search_query': search_query,
                'today': timezone.now(),
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context.update({'attendances': [], 'today': timezone.now(), 'search_query': ''})
        return context

class TeacherAttendanceReportView(TemplateView):
    template_name = 'academics/teacher_attendance_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            attendances = TeacherAttendance.objects.all().order_by('-date', 'teacher__name')
            search_query = self.request.GET.get('q', '').strip()
            if search_query:
                attendances = attendances.filter(teacher__name__icontains=search_query)

            context.update({
                'attendances': attendances,
                'search_query': search_query,
                'today': timezone.now(),
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context.update({'attendances': [], 'today': timezone.now(), 'search_query': ''})
        return context

class SalaryPayslipView(TemplateView):
    template_name = 'academics/salary_payslip.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            salary_id = self.kwargs.get('pk')
            salary = TeacherSalary.objects.get(id=salary_id)
            
            context.update({
                'salary': salary,
                'today': timezone.now(),
            })
        except TeacherSalary.DoesNotExist:
            messages.error(self.request, "سجل الراتب غير موجود.")
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
        return context

class AboutView(TemplateView):
    template_name = 'academics/about.html'

class ContactView(TemplateView):
    template_name = 'academics/contact.html'

# ==========================================
# 11. إدارة الشُعب
# ==========================================
class SchoolClassListView(TemplateView):
    template_name = 'academics/class_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['classes'] = SchoolClass.objects.all().order_by('grade__name', 'section')
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context['classes'] = []
        return context

class SchoolClassCreateView(View):
    def get(self, request):
        return render(request, 'academics/class_form.html', {'grades': Grade.objects.all()})

    def post(self, request):
        try:
            grade_id = request.POST.get('grade')
            section = request.POST.get('section')
            if grade_id and section:
                grade = Grade.objects.get(id=grade_id)
                if SchoolClass.objects.filter(grade=grade, section=section).exists():
                    messages.warning(request, "هذه الشعبة موجودة بالفعل.")
                else:
                    SchoolClass.objects.create(grade=grade, section=section)
                    messages.success(request, "تمت إضافة الشعبة بنجاح!")
                    return redirect('class_list')
            else:
                messages.error(request, "الرجاء ملء جميع الحقول.")
        except Exception as e:
            messages.error(request, f"فشل في الإضافة: {str(e)}")
        return redirect('class_add')

class SchoolClassDeleteView(DeleteView):
    model = SchoolClass
    template_name = 'academics/class_confirm_delete.html'
    success_url = reverse_lazy('class_list')

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(request, "تم حذف الشعبة بنجاح!")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('class_list')

# ==========================================
# 12. الجدول الأسبوعي
# ==========================================
class WeeklyScheduleListView(TemplateView):
    template_name = 'academics/schedule_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            schedules = WeeklySchedule.objects.all().order_by('day', 'period')
            
            # البحث
            search_query = self.request.GET.get('q', '').strip()
            if search_query:
                schedules = schedules.filter(
                    Q(teacher__name__icontains=search_query) |
                    Q(subject__name__icontains=search_query) |
                    Q(school_class__grade__name__icontains=search_query) |
                    Q(school_class__section__icontains=search_query)
                )
            
            context['schedules'] = schedules
            context['search_query'] = search_query
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context['schedules'] = []
        return context

class WeeklyScheduleCreateView(View):
    def get(self, request):
        context = {
            'days': WeeklySchedule.DAY_CHOICES,
            'periods': WeeklySchedule.PERIOD_CHOICES,
            'classes': SchoolClass.objects.all(),
            'subjects': Subject.objects.all(),
            'teachers': Teacher.objects.filter(is_active=True),
        }
        return render(request, 'academics/schedule_form.html', context)

    def post(self, request):
        try:
            day = request.POST.get('day')
            period = request.POST.get('period')
            class_id = request.POST.get('school_class')
            subject_id = request.POST.get('subject')
            teacher_id = request.POST.get('teacher')

            if not all([day, period, class_id, subject_id, teacher_id]):
                messages.warning(request, "الرجاء ملء جميع الحقول.")
                return redirect('schedule_add')

            school_class = SchoolClass.objects.get(id=class_id)
            subject = Subject.objects.get(id=subject_id)
            teacher = Teacher.objects.get(id=teacher_id)

            if WeeklySchedule.objects.filter(day=day, period=period, school_class=school_class).exists():
                messages.warning(request, "هذه الحصة محجوزة بالفعل لهذه الشعبة في هذا الوقت.")
            else:
                WeeklySchedule.objects.create(
                    day=day, period=period, school_class=school_class, subject=subject, teacher=teacher
                )
                messages.success(request, "تمت إضافة الحصة للجدول بنجاح!")
            return redirect('schedule_list')
        except Exception as e:
            messages.error(request, f"فشل في الإضافة: {str(e)}")
            return redirect('schedule_add')

class WeeklyScheduleDeleteView(DeleteView):
    model = WeeklySchedule
    template_name = 'academics/schedule_confirm_delete.html'
    success_url = reverse_lazy('schedule_list')

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(request, "تم حذف الحصة من الجدول بنجاح!")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('schedule_list')

# ==========================================
# 13. الحضور اليومي الذكي
# ==========================================
class DailyAttendanceView(TemplateView):
    template_name = 'academics/daily_attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # استخدام timezone.localdate() لضمان جلب تاريخ اليوم الصحيح
            today_date = timezone.localdate() 
            
            day_name_ar = {
                0: 'الاثنين', 1: 'الثلاثاء', 2: 'الأربعاء',
                3: 'الخميس', 4: 'الجمعة', 5: 'السبت', 6: 'الأحد'
            }.get(today_date.weekday(), 'الأحد')

            # جلب الحصص
            today_schedules = WeeklySchedule.objects.filter(day=day_name_ar).order_by('period')
            
            # جلب الحضور المسجل مسبقاً
            attendance_today = {a.teacher_id: a for a in TeacherAttendance.objects.filter(date=today_date)}

            schedule_data = []
            for schedule in today_schedules:
                att = attendance_today.get(schedule.teacher.id)
                schedule_data.append({
                    'schedule': schedule,
                    'status': att.status if att else 'حاضر',
                    'note': att.note if att else ''
                })

            context.update({
                'today': today_date,
                'day_name': day_name_ar,
                'schedule_data': schedule_data,
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context.update({'today': timezone.now(), 'day_name': '', 'schedule_data': []})
        return context

    def post(self, request):
        try:
            today = timezone.localdate()
            teacher_ids = request.POST.getlist('teacher_id[]')
            statuses = request.POST.getlist('status[]')
            notes = request.POST.getlist('note[]')

            for i in range(len(teacher_ids)):
                if teacher_ids[i] and statuses[i]:
                    teacher = Teacher.objects.get(id=teacher_ids[i])
                    TeacherAttendance.objects.update_or_create(
                        teacher=teacher, date=today,
                        defaults={'status': statuses[i], 'note': notes[i]}
                    )
            messages.success(request, "تم حفظ حضور اليوم بنجاح!")
            return redirect('daily_attendance')
        except Exception as e:
            messages.error(request, f"فشل في حفظ الحضور: {str(e)}")
            return redirect('daily_attendance')
        
# ==========================================
# 14. تعديل الحصة في الجدول الأسبوعي
# ==========================================
class WeeklyScheduleUpdateView(View):
    def get(self, request, pk):
        try:
            schedule = WeeklySchedule.objects.get(id=pk)
            context = {
                'object': schedule,
                'days': WeeklySchedule.DAY_CHOICES,
                'periods': WeeklySchedule.PERIOD_CHOICES,
                'classes': SchoolClass.objects.all(),
                'subjects': Subject.objects.all(),
                'teachers': Teacher.objects.filter(is_active=True),
                'is_update': True
            }
            return render(request, 'academics/schedule_form.html', context)
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            return redirect('schedule_list')

    def post(self, request, pk):
        try:
            schedule = WeeklySchedule.objects.get(id=pk)
            schedule.day = request.POST.get('day')
            schedule.period = request.POST.get('period')
            schedule.school_class = SchoolClass.objects.get(id=request.POST.get('school_class'))
            schedule.subject = Subject.objects.get(id=request.POST.get('subject'))
            schedule.teacher = Teacher.objects.get(id=request.POST.get('teacher'))
            schedule.save()
            
            messages.success(self.request, "تم تعديل الحصة بنجاح!")
            return redirect('schedule_list')
        except Exception as e:
            messages.error(self.request, f"فشل في التعديل: {str(e)}")
            return redirect('schedule_update', pk=pk)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class DashboardStatsAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # 1. عدد الطلاب النشطين
            total_students = Student.objects.filter(is_active=True).count()
            
            # 2. عدد المعلمين النشطين
            total_teachers = Teacher.objects.filter(is_active=True).count()
            
            # 3. إجمالي الديون
            students = Student.objects.filter(is_active=True)
            total_debts = sum((s.balance for s in students), Decimal('0.00'))

            return Response({
                'students': total_students,
                'teachers': total_teachers,
                'debts': float(total_debts),
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)