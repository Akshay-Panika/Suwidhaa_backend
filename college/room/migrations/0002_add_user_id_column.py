from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("room", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE "room_room"
                ADD COLUMN IF NOT EXISTS "user_id" varchar(255);
            """,
            reverse_sql="""
                ALTER TABLE "room_room"
                DROP COLUMN IF EXISTS "user_id";
            """,
        ),
    ]