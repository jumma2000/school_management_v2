from django.db import migrations
from decimal import Decimal

def add_pricing(apps, schema_editor):
    # استدعاء الموديلات
    Grade = apps.get_model('academics', 'Grade')
    Subject = apps.get_model('academics', 'Subject')
    ClassPricing = apps.get_model('academics', 'ClassPricing')

    # السعر الافتراضي للحصة (يمكنك تغييره لاحقاً من الواجهة)
    DEFAULT_PRICE = Decimal('15.00') 

    all_grades = Grade.objects.all()

    for grade in all_grades:
        # تحديد المرحلة بناءً على اسم الصف
        if "الابتدائي" in grade.name:
            stage = 'ابتدائي'
        elif "الإعدادي" in grade.name:
            stage = 'إعدادي'
        elif "الثانوي" in grade.name:
            stage = 'ثانوي'
        else:
            stage = 'ابتدائي' # افتراضي

        # جلب مواد هذا الصف
        subjects = Subject.objects.filter(grade=grade)

        for subject in subjects:
            # إضافة التسعير إذا لم يكن موجوداً
            ClassPricing.objects.get_or_create(
                stage=stage,
                grade=grade,
                subject=subject,
                defaults={'price_per_class': DEFAULT_PRICE}
            )

class Migration(migrations.Migration):

    dependencies = [
        # اسم الملف السابق (الخاص بالمواد)
        ('academics', '0004_add_default_subjects'), 
    ]

    operations = [
        migrations.RunPython(add_pricing),
    ]
    