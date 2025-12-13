import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rightOnTime.settings')
django.setup()

from django.db import connection

def add_missing_columns():
    """Agrega todas las columnas faltantes a la tabla employees_employee"""
    with connection.cursor() as cursor:
        try:
            # Primero, obtener las columnas actuales
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'employees_employee';
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            print(f"Columnas existentes: {', '.join(existing_columns)}\n")
            
            # Definir todas las columnas que deberían existir
            columns_to_add = [
                ("role", "VARCHAR(50) DEFAULT 'Employee'"),
                ("contract_date", "DATE NULL"),
                ("state", "VARCHAR(20) DEFAULT 'active'"),
                ("email", "VARCHAR(200) UNIQUE NULL"),
                ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
                ("updated_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
            ]
            
            # Agregar cada columna si no existe
            for column_name, column_definition in columns_to_add:
                if column_name not in existing_columns:
                    sql = f"""
                    ALTER TABLE employees_employee 
                    ADD COLUMN {column_name} {column_definition};
                    """
                    cursor.execute(sql)
                    print(f"✓ Columna '{column_name}' agregada exitosamente")
                else:
                    print(f"- Columna '{column_name}' ya existe")
            
            # Verificar columnas finales
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'employees_employee'
                ORDER BY ordinal_position;
            """)
            final_columns = [row[0] for row in cursor.fetchall()]
            print(f"\n✓ Columnas finales: {', '.join(final_columns)}")
                
        except Exception as e:
            print(f"✗ Error al agregar columnas: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("Agregando columnas faltantes a la tabla employees_employee...\n")
    if add_missing_columns():
        print("\n¡Listo! Ahora puedes crear empleados.")
    else:
        print("\nHubo un problema. Revisa el error anterior.")
