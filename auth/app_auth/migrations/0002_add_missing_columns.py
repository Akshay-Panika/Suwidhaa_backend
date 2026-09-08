from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                """
                ALTER TABLE app_auth_user 
                ADD COLUMN IF NOT EXISTS name VARCHAR(100) NOT NULL DEFAULT '',
                ADD COLUMN IF NOT EXISTS phone_number VARCHAR(15) NOT NULL DEFAULT '',
                ADD COLUMN IF NOT EXISTS is_logged_in BOOLEAN NOT NULL DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                """
            ],
            reverse_sql=[
                "ALTER TABLE app_auth_user DROP COLUMN IF EXISTS name, DROP COLUMN IF EXISTS phone_number, DROP COLUMN IF EXISTS is_logged_in, DROP COLUMN IF EXISTS created_at, DROP COLUMN IF EXISTS updated_at"
            ],
        ),
    ]