import psycopg2

DB_URL = "postgresql://suwidhaa_backend_db_v3_user:z61Z17fHify7YL1Lr6VLt01wi3Ascfvb@dpg-dbacjtbbc2fs73ast8sg-a.oregon-postgres.render.com/suwidhaa_backend_db_v3"

try:
    print("Connecting to Render Database...")
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cursor = conn.cursor()

    # 1. History clear karein
    cursor.execute("DELETE FROM django_migrations WHERE app = 'transport';")
    
    # 2. Tables drop karein (agar bachi hui hain toh)
    cursor.execute("DROP TABLE IF EXISTS transport_transportstudent CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS transport_transport CASCADE;")

    print("✅ Render Database cleared successfully!")
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error aaya: {e}")