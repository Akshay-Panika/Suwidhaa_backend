# school/classes/migrations/0004_remove_school_name_and_apply_unique.py
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0003_copy_school_names'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='class',
            options={'ordering': ['-id']},
        ),
        migrations.AlterUniqueTogether(
            name='class',
            unique_together={('class_name', 'school')},
        ),
        migrations.RemoveField(
            model_name='class',
            name='school_name',
        ),
    ]