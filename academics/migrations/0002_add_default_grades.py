from django.db import migrations

def add_grades(apps, schema_editor):
    # استدعاء موديل Grade
    Grade = apps.get_model('academics', 'Grade')
    
    # قائمة الصفوف الدراسية المطلوبة
    grades_list = [
        # المرحلة الابتدائية
        "الصف الأول الابتدائي",
        "الصف الثاني الابتدائي",
        "الصف الثالث الابتدائي",
        "الصف الرابع الابتدائي",
        "الصف الخامس الابتدائي",
        "الصف السادس الابتدائي",
        
        # المرحلة الإعدادية
        "الصف الأول الإعدادي",
        "الصف الثاني الإعدادي",
        "الصف الثالث الإعدادي",
        
        # المرحلة الثانوية
        "الصف الأول الثانوي",
        "الصف الثاني الثانوي",
        "الصف الثالث الثانوي",
    ]

    # إدخال الصفوف في قاعدة البيانات
    for grade_name in grades_list:
        # get_or_create تضمن عدم تكرار الصف إذا كان موجوداً
        Grade.objects.get_or_create(name=grade_name)

class Migration(migrations.Migration):

    dependencies = [
        # اسم ملف الترحيل السابق (غالباً سيكون 0001_initial)
        # تأكد من كتابة اسم الملف السابق بالضبط
        ('academics', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(add_grades),
    ]