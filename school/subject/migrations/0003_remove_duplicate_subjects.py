from django.db import migrations


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
        ('subject', '0002_alter_subject_subject_name'),   # ✅ yahi fix hai
    ]

    operations = [
        migrations.RunPython(remove_duplicates, reverse_func),
    ]