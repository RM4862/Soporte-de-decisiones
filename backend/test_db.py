import mysql.connector
from mysql.connector import Error

SG_DB = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'SG_Proyectos'
}

try:
    conn = mysql.connector.connect(**SG_DB)
    cursor = conn.cursor(dictionary=True)
    
    print("=== TABLAS EN LA BASE DE DATOS ===")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        print(table)
    
    print("\n=== ESTRUCTURA DE PROYECTOS ===")
    cursor.execute("DESCRIBE Proyectos")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col['Field']}: {col['Type']}")
    
    print("\n=== ESTRUCTURA DE DEFECTOS ===")
    cursor.execute("DESCRIBE Defectos")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col['Field']}: {col['Type']}")
    
    print("\n=== ESTRUCTURA DE EVALUACIONES_CLIENTE ===")
    cursor.execute("DESCRIBE evaluaciones_cliente")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col['Field']}: {col['Type']}")
    
    print("\n=== TEST QUERY: Proyectos Activos ===")
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM Proyectos 
        WHERE estado IN ('En Desarrollo', 'Testing', 'En Progreso')
    """)
    result = cursor.fetchone()
    print(f"Proyectos activos: {result['total']}")
    
    cursor.close()
    conn.close()
    print("\n✅ Conexión exitosa!")
    
except Error as e:
    print(f"❌ Error: {e}")
