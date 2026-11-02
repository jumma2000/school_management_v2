from django.db import migrations

def add_subjects(apps, schema_editor):
    # استدعاء الموديلات
    Grade = apps.get_model('academics', 'Grade')
    Subject = apps.get_model('academics', 'Subject')

    # 1. المواد الخاصة بالمرحلة الابتدائية
    primary_subjects = [
        "اللغة العربية", "التربية الإسلامية", "الرياضيات", 
        "العلوم", "اللغة الإنجليزية", "التربية الوطنية", "الخط والإملاء"
    ]

    # 2. المواد الخاصة بالمرحلة الإعدادية
    middle_subjects = [
        "اللغة العربية", "التربية الإسلامية", "الرياضيات", 
        "العلوم", "اللغة الإنجليزية", "الدراسات الاجتماعية", "الحاسوب"
    ]

    # 3. المواد الخاصة بالمرحلة الثانوية (القسم العلمي والأدبي)
    high_subjects = [
        "اللغة العربية", "التربية الإسلامية", "الرياضيات", 
        "الفيزياء", "الكيمياء", "الأحياء", "اللغة الإنجليزية", 
        "التاريخ", "الجغرافيا", "الفلسفة", "الحاسوب"
    ]

    # جلب كل الصفوف
    all_grades = Grade.objects.all()

    for grade in all_grades:
        # تحديد المواد بناءً على اسم الصف
        if "الابتدائي" in grade.name:
            subjects_to_add = primary_subjects
        elif "الإعدادي" in grade.name:
            subjects_to_add = middle_subjects
        elif "الثانوي" in grade.name:
            subjects_to_add = high_subjects
        else:
            subjects_to_add = primary_subjects # افتراضي

        # إدخال المواد
        for subj_name in subjects_to_add:
            Subject.objects.get_or_create(
                name=subj_name,
                grade=grade
            )

class Migration(migrations.Migration):

    dependencies = [
        # اسم الملف السابق (الخاص بالشعب)
        ('academics', '0003_add_default_sections'), 
    ]

    operations = [
        migrations.RunPython(add_subjects),
    ]