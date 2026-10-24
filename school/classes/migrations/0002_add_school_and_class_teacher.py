# school/classes/migrations/0002_add_school_and_class_teacher.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0001_initial'),
        ('school_type', '0001_initial'), # Adjust if your school_type initial migration has a different name
        ('teacher', '0001_initial'),     # Adjust if your teacher initial migration has a different name
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='school',
            field=models.ForeignKey(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.CASCADE, 
                related_name='classes', 
                to='school_type.schooltype'
            ),
        ),
        migrations.AddField(
            model_name='class',
            name='class_teacher',
            field=models.ForeignKey(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                related_name='classes_as_teacher', 
                to='teacher.teacher'
            ),
        ),
    ]