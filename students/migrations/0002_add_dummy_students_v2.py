from django.db import migrations

def add_students(apps, schema_editor):
    Student = apps.get_model('students', 'Student')
    Grade = apps.get_model('academics', 'Grade')  # تم التغيير هنا

    # جلب أول صف من كل مرحلة
    primary_grade = Grade.objects.filter(name__contains="الابتدائي").first()
    middle_grade = Grade.objects.filter(name__contains="الإعدادي").first()
    high_grade = Grade.objects.filter(name__contains="الثانوي").first()

    students_data = [
        {"name": "محمد أحمد الصادق", "parent": "أحمد الصادق", "phone": "0921111111", "grade": primary_grade, "fees": 1500.00},
        {"name": "عبدالرحمن خالد المبروك", "parent": "خالد المبروك", "phone": "0922222222", "grade": primary_grade, "fees": 1500.00},
        {"name": "يوسف علي بن سعيد", "parent": "علي بن سعيد", "phone": "0923333333", "grade": primary_grade, "fees": 1500.00},
        {"name": "سارة عمر الفيتوري", "parent": "عمر الفيتوري", "phone": "0924444444", "grade": middle_grade, "fees": 2000.00},
        {"name": "فاطمة مصطفى الشريف", "parent": "مصطفى الشريف", "phone": "0925555555", "grade": middle_grade, "fees": 2000.00},
        {"name": "مريم إبراهيم القذافي", "parent": "إبراهيم القذافي", "phone": "0926666666", "grade": middle_grade, "fees": 2000.00},
        {"name": "عمر سالم الزوي", "parent": "سالم الزوي", "phone": "0927777777", "grade": high_grade, "fees": 2500.00},
        {"name": "أيمن صالح الدرسي", "parent": "صالح الدرسي", "phone": "0928888888", "grade": high_grade, "fees": 2500.00},
        {"name": "حسين طارق بالحاج", "parent": "طارق بالحاج", "phone": "0929999999", "grade": high_grade, "fees": 2500.00},
        {"name": "ليلى عبدالله القمودي", "parent": "عبدالله القمودي", "phone": "0920000000", "grade": primary_grade, "fees": 1500.00},
    ]

    for data in students_data:
        if data["grade"]:
            Student.objects.get_or_create(
                name=data["name"],
                defaults={
                    'parent_name': data["parent"],
                    'phone': data["phone"],
                    'grade': data["grade"],  # تم التعديل هنا
                    'total_fees': data["fees"],
                    'is_active': True,
                }
            )
            print(f"✅ تمت إضافة: {data['name']}")

class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0007_add_smart_schedule'), 
        ('students', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(add_students),
    ]
