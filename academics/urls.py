from django.urls import path
from .views import DashboardStatsAPI # تأكد من الاستيراد
from .views import (
    DashboardView, AboutView, ContactView,BackupDatabaseView,
    GradeListView, 
    GradeCreateView, 
    GradeUpdateView, 
    GradeDeleteView, 
    DebtReportView,
    PaymentHistoryView,BackupDatabaseView,DebtReportPDFView,
    # --- استدعاء كلاسات المعلمين ---
    TeacherListView, TeacherCreateView, TeacherUpdateView,TeacherDeleteView, 
    PricingListView, PricingCreateView,
    SalaryCreateView, SalaryListView,PricingUpdateView,
    PricingDeleteView,StudentDataReportView,TeacherDataReportView,SubjectListView,
    SubjectCreateView,SubjectUpdateView,SubjectDeleteView,TeacherAttendanceView ,
    StudentAttendanceReportView,TeacherAttendanceReportView,SalaryPayslipView,
    SchoolClassListView,SchoolClassCreateView,SchoolClassDeleteView,
    WeeklyScheduleListView,WeeklyScheduleCreateView,WeeklyScheduleDeleteView,
    DailyAttendanceView,WeeklyScheduleUpdateView,

)   
urlpatterns = [
    # --- الرئيسية والصفوف ---
    path('', DashboardView.as_view(), name='home'),
    path('grades/', GradeListView.as_view(), name='grade_list'),
    path('grades/add/', GradeCreateView.as_view(), name='grade_add'),
    path('grades/<int:pk>/edit/', GradeUpdateView.as_view(), name='grade_update'),
    path('grades/<int:pk>/delete/', GradeDeleteView.as_view(), name='grade_delete'),
    
    # --- التقارير ---
    path('reports/debts/', DebtReportView.as_view(), name='debt_report'), 
    
    # --- المعلمين ---
    path('teachers/', TeacherListView.as_view(), name='teacher_list'),
    path('teachers/add/', TeacherCreateView.as_view(), name='teacher_add'),
    path('teachers/<int:pk>/edit/', TeacherUpdateView.as_view(), name='teacher_update'),
    path('teachers/<int:pk>/delete/', TeacherDeleteView.as_view(), name='teacher_delete'),
    path('payments/history/', PaymentHistoryView.as_view(), name='payment_history'), # <--- جديد
    path('pricing/', PricingListView.as_view(), name='pricing_list'),
    path('pricing/add/', PricingCreateView.as_view(), name='pricing_add'),
    path('teachers/<int:teacher_id>/salary/add/', SalaryCreateView.as_view(), name='salary_add'),
    path('salaries/', SalaryListView.as_view(), name='salary_list'),
    path('pricing/<int:pk>/edit/', PricingUpdateView.as_view(), name='pricing_update'),
    path('pricing/<int:pk>/delete/', PricingDeleteView.as_view(), name='pricing_delete'),

    path('reports/students-data/', StudentDataReportView.as_view(), name='student_data_report'),
    path('reports/teachers-data/', TeacherDataReportView.as_view(), name='teacher_data_report'),

     # --- المواد الدراسية ---
    path('subjects/', SubjectListView.as_view(), name='subject_list'),
    path('subjects/add/', SubjectCreateView.as_view(), name='subject_add'),
    path('subjects/<int:pk>/edit/', SubjectUpdateView.as_view(), name='subject_update'),
    path('subjects/<int:pk>/delete/', SubjectDeleteView.as_view(), name='subject_delete'),
    path('teachers/attendance/', TeacherAttendanceView.as_view(), name='teacher_attendance'), # <--- جديد
    path('reports/students-attendance/', StudentAttendanceReportView.as_view(), name='student_attendance_report'),
    path('reports/teachers-attendance/', TeacherAttendanceReportView.as_view(), name='teacher_attendance_report'),
    path('salaries/<int:pk>/payslip/', SalaryPayslipView.as_view(), name='salary_payslip'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('backup/', BackupDatabaseView.as_view(), name='backup'),

        # الشُعب
    path('classes/', SchoolClassListView.as_view(), name='class_list'),
    path('classes/add/', SchoolClassCreateView.as_view(), name='class_add'),
    path('classes/<int:pk>/delete/', SchoolClassDeleteView.as_view(), name='class_delete'),
    
    # الجدول الأسبوعي
    path('schedule/', WeeklyScheduleListView.as_view(), name='schedule_list'),
    path('schedule/add/', WeeklyScheduleCreateView.as_view(), name='schedule_add'),
    path('schedule/<int:pk>/delete/', WeeklyScheduleDeleteView.as_view(), name='schedule_delete'),
    
    # الحضور اليومي
    path('daily-attendance/', DailyAttendanceView.as_view(), name='daily_attendance'),
    path('schedule/<int:pk>/edit/', WeeklyScheduleUpdateView.as_view(), name='schedule_update'),
    path('backup/', BackupDatabaseView.as_view(), name='backup_db'), # <--- أضف هذا السطر
    path('reports/debts/pdf/', DebtReportPDFView.as_view(), name='debt_report_pdf'),
    path('api/dashboard/', DashboardStatsAPI.as_view(), name='api_dashboard'),    
]
