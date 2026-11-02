from django.db import migrations

def add_sections(apps, schema_editor):
    # استدعاء الموديلات
    Grade = apps.get_model('academics', 'Grade')
    SchoolClass = apps.get_model('academics', 'SchoolClass')

    # الشُعب المطلوبة
    sections = ['أ', 'ب', 'ج', 'د']

    # جلب كل الصفوف الموجودة في قاعدة البيانات
    all_grades = Grade.objects.all()

    for grade in all_grades:
        for section in sections:
            # get_or_create تضمن عدم التكرار
            SchoolClass.objects.get_or_create(
                grade=grade,
                section=section
            )

class Migration(migrations.Migration):

    dependencies = [
        # تأكد من أن هذا هو اسم الملف السابق الذي أنشأناه (0002)
        ('academics', '0002_add_default_grades'), 
    ]

    operations = [
        migrations.RunPython(add_sections),
    ]