from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0002_add_missing_columns'),
    ]

    operations = [
        # First drop the existing table
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS app_auth_user CASCADE;",
            reverse_sql="CREATE TABLE app_auth_user (id INTEGER PRIMARY KEY);"
        ),
        # Then recreate it using Django's schema
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('is_logged_in', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'app_auth_user',
                'ordering': ['-created_at'],
            },
        ),
    ]