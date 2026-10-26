from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE event_schoolevent 
            ADD COLUMN IF NOT EXISTS school_id integer 
            REFERENCES school_type_schooltype(id) 
            ON DELETE CASCADE;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]