from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .models import Student, Payment, StudentAttendance
from academics.models import Grade
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

# ==========================================
# 1. قائمة الطلاب (مع البحث والتقسيم)
# ==========================================
class StudentListView(TemplateView):
    template_name = 'students/student_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            students_list = Student.objects.filter(is_active=True).order_by('-id')
            
            # البحث
            search_query = self.request.GET.get('q', '').strip()
            if search_query:
                students_list = students_list.filter(
                    Q(name__icontains=search_query) | 
                    Q(phone__icontains=search_query) |
                    Q(grade__name__icontains=search_query)
                )
            
            # تقسيم الصفحات: 15 طالباً في كل صفحة
            paginator = Paginator(students_list, 15) 
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context['students'] = page_obj
            context['page_obj'] = page_obj
            context['search_query'] = search_query
        except Exception as e:
            messages.error(self.request, f"حدث خطأ أثناء جلب الطلاب: {str(e)}")
            context['students'] = []
        return context

# ==========================================
# 2. إضافة طالب (مع البيانات المصرفية)
# ==========================================
class StudentCreateView(View):
    def get(self, request):
        try:
            grades = Grade.objects.all()
            return render(request, 'students/student_form.html', {'grades': grades})
        except Exception as e:
            messages.error(request, "حدث خطأ في تحميل الصفحة.")
            return redirect('student_list')

    def post(self, request):
        try:
            name = request.POST.get('name')
            grade_id = request.POST.get('grade')
            parent_name = request.POST.get('parent_name', '')
            phone = request.POST.get('phone', '')
            total_fees_str = request.POST.get('total_fees', '0')
            discount_str = request.POST.get('discount', '0')

            # البيانات المصرفية
            bank_name = request.POST.get('bank_name', '')
            bank_branch = request.POST.get('bank_branch', '')
            account_number = request.POST.get('account_number', '') # <--- جديد
            bank_account = request.POST.get('bank_account', '')
            account_holder = request.POST.get('account_holder', '')

            if not name or not grade_id:
                messages.warning(request, "الرجاء إدخال اسم الطالب واختيار الصف.")
                return redirect('student_add')

            try:
                total_fees = Decimal(total_fees_str or '0')
                discount = Decimal(discount_str or '0')
            except:
                total_fees = Decimal('0.00')
                discount = Decimal('0.00')

            grade = Grade.objects.get(id=grade_id)

            Student.objects.create(
                name=name, grade=grade, parent_name=parent_name, phone=phone,
                total_fees=total_fees, discount=discount,
                bank_name=bank_name, bank_branch=bank_branch, 
                account_number=account_number, # <--- جديد
                bank_account=bank_account, account_holder=account_holder
            )
            messages.success(request, "تمت إضافة الطالب بنجاح!")
            return redirect('student_list')

        except Exception as e:
            messages.error(request, f"فشل في إضافة الطالب. تفاصيل: {str(e)}")
            return redirect('student_add')

# ==========================================
# 3. تسجيل دفعة (سداد)
# ==========================================
class PaymentCreateView(View):
    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            return render(request, 'students/payment_form.html', {'student': student})
        except Student.DoesNotExist:
            messages.error(request, "الطالب غير موجود.")
            return redirect('student_list')
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('student_list')

    def post(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            amount_str = request.POST.get('amount', '0')
            
            try:
                amount = Decimal(amount_str or '0')
            except:
                amount = Decimal('0.00')
                
            if amount <= 0:
                messages.warning(request, "الرجاء إدخال مبلغ صحيح أكبر من صفر.")
                return render(request, 'students/payment_form.html', {'student': student})

            Payment.objects.create(
                student=student, amount=amount, note=request.POST.get('note', '')
            )
            messages.success(request, f"تم تسجيل دفعة بمبلغ {amount} للطالب {student.name} بنجاح!")
            return redirect('student_list')
            
        except Exception as e:
            messages.error(request, f"فشل تسجيل الدفعة. تفاصيل: {str(e)}")
            return render(request, 'students/payment_form.html', {'student': student})

# ==========================================
# 4. تعديل بيانات طالب (مع البيانات المصرفية)
# ==========================================
class StudentUpdateView(View):
    def get(self, request, pk):
        try:
            student = Student.objects.get(id=pk)
            grades = Grade.objects.all()
            return render(request, 'students/student_form.html', {
                'object': student, 'grades': grades, 'is_update': True
            })
        except Student.DoesNotExist:
            messages.error(request, "الطالب غير موجود.")
            return redirect('student_list')
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('student_list')

    def post(self, request, pk):
        try:
            student = Student.objects.get(id=pk)
            name = request.POST.get('name')
            grade_id = request.POST.get('grade')
            parent_name = request.POST.get('parent_name', '')
            phone = request.POST.get('phone', '')
            total_fees_str = request.POST.get('total_fees', '0')
            discount_str = request.POST.get('discount', '0')

            if not name or not grade_id:
                messages.warning(request, "الرجاء إدخال اسم الطالب واختيار الصف.")
                return redirect('student_update', pk=pk)

            try:
                total_fees = Decimal(total_fees_str or '0')
                discount = Decimal(discount_str or '0')
            except:
                total_fees = Decimal('0.00')
                discount = Decimal('0.00')

            grade = Grade.objects.get(id=grade_id)

            # حفظ البيانات
            student.name = name
            student.grade = grade
            student.parent_name = parent_name
            
            if phone:
                student.phone = phone
                
            student.total_fees = total_fees
            student.discount = discount

            # تحديث البيانات المصرفية
            student.bank_name = request.POST.get('bank_name', student.bank_name)
            student.bank_branch = request.POST.get('bank_branch', student.bank_branch)
            student.account_number = request.POST.get('account_number', student.account_number) # <--- جديد
            student.bank_account = request.POST.get('bank_account', student.bank_account)
            student.account_holder = request.POST.get('account_holder', student.account_holder)

            student.save()

            messages.success(request, "تم تعديل بيانات الطالب بنجاح!")
            return redirect('student_list')

        except Student.DoesNotExist:
            messages.error(request, "الطالب غير موجود.")
            return redirect('student_list')
        except Exception as e:
            messages.error(request, f"فشل في تعديل الطالب: {str(e)}")
            return redirect('student_update', pk=pk)

# ==========================================
# 5. حذف طالب
# ==========================================
class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(request, "تم حذف الطالب بنجاح!")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء الحذف: {str(e)}")
            return redirect('student_list')

# ==========================================
# 6. سجل حضور الطلاب (عرض وتسجيل)
# ==========================================
class StudentAttendanceView(TemplateView):
    template_name = 'students/attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            students = Student.objects.filter(is_active=True).order_by('grade__name', 'name')
            today = timezone.now().date()
            attendance_today = {a.student_id: a for a in StudentAttendance.objects.filter(date=today)}
            
            # تجهيز القائمة لتفادي أخطاء القالب
            students_with_status = []
            for student in students:
                attendance = attendance_today.get(student.id)
                students_with_status.append({
                    'student': student,
                    'status': attendance.status if attendance else 'حاضر',
                    'note': attendance.note if attendance else ''
                })

            context.update({
                'students_with_status': students_with_status,
                'today': today,
            })
        except Exception as e:
            messages.error(self.request, f"حدث خطأ: {str(e)}")
            context.update({'students_with_status': [], 'today': timezone.now()})
        return context

    def post(self, request):
        try:
            today = timezone.now().date()
            student_ids = request.POST.getlist('student_id[]')
            statuses = request.POST.getlist('status[]')
            notes = request.POST.getlist('note[]')

            for i in range(len(student_ids)):
                if student_ids[i] and statuses[i]:
                    student = Student.objects.get(id=student_ids[i])
                    StudentAttendance.objects.update_or_create(
                        student=student, date=today,
                        defaults={'status': statuses[i], 'note': notes[i]}
                    )
            messages.success(request, "تم حفظ سجل الحضور بنجاح!")
            return redirect('student_attendance')
        except Exception as e:
            messages.error(request, f"فشل في حفظ الحضور: {str(e)}")
            return redirect('student_attendance')