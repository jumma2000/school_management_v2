from django.db import migrations

def create_smart_schedule(apps, schema_editor):
    Teacher = apps.get_model('academics', 'Teacher')
    Subject = apps.get_model('academics', 'Subject')
    SchoolClass = apps.get_model('academics', 'SchoolClass')
    WeeklySchedule = apps.get_model('academics', 'WeeklySchedule')

    # 1. تحديد الشعبة (أول شعبة في النظام)
    target_class = SchoolClass.objects.first()
    if not target_class:
        return

    # 2. جلب مواد هذه الشعبة وتحويلها إلى قائمة عادية
    subjects_qs = Subject.objects.filter(grade=target_class.grade)
    if not subjects_qs.exists():
        return
        
    # تحويل المواد إلى قائمة (List) لسهولة التدوير
    subjects_list = list(subjects_qs)
    
    # 3. الأيام والحصص
    days = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس']
    periods = ['الأولى', 'الثانية', 'الثالثة', 'الرابعة', 'الخامسة']

    # 4. بناء الجدول
    subject_index = 0 # مؤشر للمادة الحالية
    
    for day in days:
        for period in periods:
            # اختيار المادة بناءً على المؤشر
            subject = subjects_list[subject_index % len(subjects_list)]
            
            # البحث عن معلم يطابق تخصص المادة
            teacher = Teacher.objects.filter(subject=subject.name).first()
            
            # إذا لم يجد معلماً بهذا التخصص، يختار أول معلم متاح
            if not teacher:
                teacher = Teacher.objects.first()

            if teacher:
                WeeklySchedule.objects.get_or_create(
                    day=day,
                    period=period,
                    school_class=target_class,
                    defaults={
                        'subject': subject,
                        'teacher': teacher
                    }
                )
            
            # الانتقال للمادة التالية
            subject_index += 1

class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0006_add_dummy_teachers'), 
    ]

    operations = [
        migrations.RunPython(create_smart_schedule),
    ]
    