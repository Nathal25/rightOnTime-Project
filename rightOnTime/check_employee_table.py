import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rightOnTime.settings')
django.setup()

from django.db import connection

def check_table_structure():
    """Verifica la estructura de la tabla employees_employee"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee' 
            ORDER BY ordinal_position;
        """)
        
        print("Estructura actual de employees_employee:\n")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} | NULL: {row[2]} | Default: {row[3]}")

if __name__ == '__main__':
    check_table_structure()
