from django.db import migrations

def add_teachers(apps, schema_editor):
    Teacher = apps.get_model('academics', 'Teacher')

    # قائمة المعلمين الوهميين (الاسم، التخصص، رقم الهاتف)
    teachers_data = [
        {"name": "أحمد محمد علي", "subject": "اللغة العربية", "phone": "0910000001"},
        {"name": "خالد عبدالسلام", "subject": "الرياضيات", "phone": "0910000002"},
        {"name": "عمر يوسف الفيتوري", "subject": "اللغة الإنجليزية", "phone": "0910000003"},
        {"name": "سالم إبراهيم القذافي", "subject": "العلوم", "phone": "0910000004"},
        {"name": "محمد مصطفى الشريف", "subject": "التربية الإسلامية", "phone": "0910000005"},
        {"name": "علي حسين الزوي", "subject": "الدراسات الاجتماعية", "phone": "0910000006"},
        {"name": "يوسف بشير المبروك", "subject": "الفيزياء", "phone": "0910000007"},
        {"name": "عبدالله نوري القمودي", "subject": "الكيمياء", "phone": "0910000008"},
        {"name": "أيمن صالح الدرسي", "subject": "الأحياء", "phone": "0910000009"},
        {"name": "طارق منصور بالحاج", "subject": "الحاسوب", "phone": "0910000010"},
    ]

    for data in teachers_data:
        # get_or_create لمنع التكرار إذا قمت بتشغيل السكربت مرتين
        Teacher.objects.get_or_create(
            name=data["name"],
            defaults={
                'subject': data["subject"],
                'phone': data["phone"],
                'is_active': True,
                'bank_name': 'مصرف الجمهورية',
                'bank_branch': 'الفرع الرئيسي',
                'account_holder': data["name"],
            }
        )

class Migration(migrations.Migration):

    dependencies = [
        # تأكد أن هذا هو اسم الملف السابق
        ('academics', '0005_add_default_pricing'), 
    ]

    operations = [
        migrations.RunPython(add_teachers),
    ]
    