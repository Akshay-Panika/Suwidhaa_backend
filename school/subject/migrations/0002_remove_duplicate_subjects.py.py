from django.db import migrations, models


def remove_duplicates(apps, schema_editor):
    Subject = apps.get_model('subject', 'Subject')

    seen = set()
    duplicates = []

    for subject in Subject.objects.all().order_by('id'):
        name_lower = subject.subject_name.strip().lower()
        if name_lower in seen:
            duplicates.append(subject.id)
        else:
            seen.add(name_lower)

    if duplicates:
        Subject.objects.filter(id__in=duplicates).delete()


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('subject', '0001_initial'),
    ]

    operations = [
        # ✅ PEHLE duplicates delete karo
        migrations.RunPython(remove_duplicates, reverse_func),

        # ✅ PHIR unique constraint lagao
        migrations.AlterField(
            model_name='subject',
            name='subject_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]