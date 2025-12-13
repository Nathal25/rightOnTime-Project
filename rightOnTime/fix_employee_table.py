import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rightOnTime.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def fix_employee_table():
    """Recrear la tabla employees_employee sin las columnas de AbstractUser"""
    
    print("🔧 Iniciando corrección de la tabla employees_employee...\n")
    
    with connection.cursor() as cursor:
        try:
            # 1. Eliminar tablas relacionadas (CASCADE eliminará las FK)
            print("1. Eliminando tablas...")
            cursor.execute("DROP TABLE IF EXISTS attendance_attendance CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS employees_employee CASCADE;")
            print("   ✓ Tablas eliminadas\n")
            
            # 2. Limpiar registros de migraciones de employees y attendance
            print("2. Limpiando registros de migraciones...")
            cursor.execute("DELETE FROM django_migrations WHERE app = 'employees';")
            cursor.execute("DELETE FROM django_migrations WHERE app = 'attendance';")
            print("   ✓ Registros de migraciones eliminados\n")
            
        except Exception as e:
            print(f"   ✗ Error: {e}\n")
            return False
    
    try:
        # 3. Eliminar migraciones antiguas de employees
        print("3. Eliminando migraciones antiguas de employees...")
        import glob
        import shutil
        migrations_path = 'employees/migrations'
        old_migrations = glob.glob(f'{migrations_path}/[0-9]*.py')
        for migration_file in old_migrations:
            os.remove(migration_file)
            print(f"   - Eliminado: {migration_file}")
        # Eliminar .pyc también
        pycache = f'{migrations_path}/__pycache__'
        if os.path.exists(pycache):
            shutil.rmtree(pycache)
        print("   ✓ Migraciones antiguas eliminadas\n")
        
        # 4. Eliminar migraciones antiguas de attendance
        print("4. Eliminando migraciones antiguas de attendance...")
        migrations_path = 'attendance/migrations'
        old_migrations = glob.glob(f'{migrations_path}/[0-9]*.py')
        for migration_file in old_migrations:
            os.remove(migration_file)
            print(f"   - Eliminado: {migration_file}")
        # Eliminar .pyc también
        pycache = f'{migrations_path}/__pycache__'
        if os.path.exists(pycache):
            shutil.rmtree(pycache)
        print("   ✓ Migraciones antiguas eliminadas\n")
        
        # 5. Recrear migraciones de employees primero
        print("5. Recreando migraciones de employees...")
        call_command('makemigrations', 'employees')
        print("   ✓ Migraciones de employees creadas\n")
        
        # 6. Aplicar migraciones de employees
        print("6. Aplicando migraciones de employees...")
        call_command('migrate', 'employees')
        print("   ✓ Migraciones de employees aplicadas\n")
        
        # 7. Recrear migraciones de attendance
        print("7. Recreando migraciones de attendance...")
        call_command('makemigrations', 'attendance')
        print("   ✓ Migraciones de attendance creadas\n")
        
        # 8. Aplicar migraciones de attendance
        print("8. Aplicando migraciones de attendance...")
        call_command('migrate', 'attendance')
        print("   ✓ Migraciones de attendance aplicadas\n")
        
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return False
    
    # 9. Verificar la estructura final
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee' 
            ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
        print("9. Verificación final - Columnas en employees_employee:")
        print(f"   {', '.join(columns)}\n")
        
        # Verificar que NO tenga columnas de AbstractUser
        user_columns = ['password', 'username', 'is_superuser', 'is_staff', 'is_active']
        has_user_columns = any(col in columns for col in user_columns)
        
        if has_user_columns:
            print("   ✗ ERROR: La tabla aún tiene columnas de AbstractUser\n")
            return False
        else:
            print("   ✓ Tabla creada correctamente (sin columnas de AbstractUser)\n")
            return True
    
    return True

if __name__ == '__main__':
    if fix_employee_table():
        print("✅ ¡Listo! Las tablas employees y attendance están correctas.")
        print("   Ahora puedes crear empleados sin problemas.")
    else:
        print("❌ Hubo un problema al corregir las tablas.")
