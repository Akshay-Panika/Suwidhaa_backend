# school/classes/migrations/0003_copy_school_names.py
from django.db import migrations

def copy_school_data(apps, schema_editor):
    Class = apps.get_model('classes', 'Class')
    SchoolType = apps.get_model('school_type', 'SchoolType')

    for cls in Class.objects.all():
        if not cls.school_id and cls.school_name:
            # Try to find a matching school by name
            school = SchoolType.objects.filter(school_name__iexact=cls.school_name.strip()).first()
            if school:
                cls.school = school
                cls.save(update_fields=['school'])

class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0002_add_school_and_class_teacher'),
    ]

    operations = [
        migrations.RunPython(copy_school_data, migrations.RunPython.noop),
    ]