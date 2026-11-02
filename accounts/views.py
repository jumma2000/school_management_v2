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
    Grade, Subject, Teacher, 
    ClassPricing, TeacherSalary, SalaryItem
)

# ==========================================
# 1. لوحة التحكم (الرئيسية)
# ==========================================
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            total_students = Student.objects.filter(is_active=True).count()
            total_teachers = Teacher.objects.filter(is_active=True).count()
            
            total_paid = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            students = Student.objects.filter(is_active=True)
            total_expected = sum((s.net_fees for s in students), Decimal('0.00'))
            total_debts = total_expected - total_paid
            
            today = timezone.now().date()
            today_paid = Payment.objects.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            recent_payments = Payment.objects.all().order_by('-date')[:5]

            context.update({
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_paid': total_paid,
                'total_debts': total_debts,
                'today_paid': today_paid,
                'recent_payments': recent_payments,
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ أثناء تحميل البيانات: {str(e)}")
            context.update({
                'total_students': 0, 'total_teachers': 0,
                'total_paid': Decimal('0.00'), 'total_debts': Decimal('0.00'), 
                'today_paid': Decimal('0.00'), 'recent_payments': []
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

class GradeUpdateView(View):
    def get(self, request, pk):
        try:
            grade = Grade.objects.get(id=pk)
            return render(request, 'academics/grade_form.html', {
                'object': grade,
                'is_update': True
            })
        except Grade.DoesNotExist:
            messages.error(request, "الصف غير موجود.")
            return redirect('grade_list')
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('grade_list')

    def post(self, request, pk):
        try:
            grade = Grade.objects.get(id=pk)
            name = request.POST.get('name')
            if name:
                grade.name = name
                grade.save()
                messages.success(request, "تم تعديل الصف بنجاح!")
                return redirect('grade_list')
            else:
                messages.error(request, "الرجاء إدخال اسم الصف.")
        except Exception as e:
            messages.error(request, f"فشل في التعديل: {str(e)}")
        return redirect('grade_update', pk=pk)

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

# ==========================================
# 4. إدارة المعلمين (مع البحث والتقسيم)
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
            
            if not name or not subject:
                messages.warning(request, "الرجاء إدخال الاسم والتخصص.")
                return redirect('teacher_add')
                
            Teacher.objects.create(name=name, subject=subject, phone=phone)
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
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            return redirect('teacher_list')

# ==========================================
# 5. سجل الدفعات (مع البحث والتقسيم)
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
# 6. إدارة تسعير الحصص (مع التقسيم)
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
# 7. إدارة الرواتب (مع البحث والتقسيم)
# ==========================================
class SalaryCreateView(View):
    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            pricings = ClassPricing.objects.all()
            months = TeacherSalary.MONTH_CHOICES
            years = TeacherSalary.YEAR_CHOICES
            return render(request, 'academics/salary_form.html', {
                'teacher': teacher,
                'pricings': pricings,
                'months': months,
                'years': years
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
    