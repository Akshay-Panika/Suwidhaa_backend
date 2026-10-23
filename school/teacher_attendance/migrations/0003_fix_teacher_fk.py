from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('teacher_attendance', '0002_remove_teacherattendance_teacher_att_date_5d9810_idx_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE teacher_attendance_teacherattendance DROP CONSTRAINT IF EXISTS teacher_attendance_t_teacher_id_d265d085_fk_auth_user;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="ALTER TABLE teacher_attendance_teacherattendance ADD CONSTRAINT teacher_attendance_teacher_id_fk FOREIGN KEY (teacher_id) REFERENCES teacher_teacher (id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;",
            reverse_sql="ALTER TABLE teacher_attendance_teacherattendance DROP CONSTRAINT IF EXISTS teacher_attendance_teacher_id_fk;",
        ),
    ]