"""
Verificar el esquema de la tabla Proyectos
para confirmar qué columnas existen
"""
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='SG_Proyectos'
)
cursor = conn.cursor()

print("=" * 80)
print("📋 ESTRUCTURA DE LA TABLA Proyectos")
print("=" * 80)

cursor.execute("DESCRIBE Proyectos")
columns = cursor.fetchall()

print(f"\n{'Campo':<35} {'Tipo':<25} {'Null':<10} {'Key':<10}")
print("-" * 80)
for col in columns:
    print(f"{col[0]:<35} {col[1]:<25} {col[2]:<10} {col[3]:<10}")

print("\n" + "=" * 80)
print("🔍 VERIFICANDO COLUMNAS RELEVANTES PARA FILTROS")
print("=" * 80)

columnas_necesarias = [
    'metodologia',
    'horas_invertidas',
    'presupuesto',
    'duracion_dias',
    'entregables_count',
    'num_tecnologias_emergentes',
    'estado',
    'fecha_inicio',
    'fecha_fin'
]

columnas_existentes = [col[0] for col in columns]

print("\n✅ Columnas que EXISTEN:")
for col in columnas_necesarias:
    if col in columnas_existentes:
        print(f"  • {col}")

print("\n❌ Columnas que NO EXISTEN:")
for col in columnas_necesarias:
    if col not in columnas_existentes:
        print(f"  • {col}")

# Mostrar algunas estadísticas
print("\n" + "=" * 80)
print("📊 ESTADÍSTICAS DE DATOS")
print("=" * 80)

cursor.execute("SELECT COUNT(*) FROM Proyectos")
total = cursor.fetchone()[0]
print(f"\n📌 Total de proyectos: {total}")

# Verificar metodologías
if 'metodologia' in columnas_existentes:
    cursor.execute("SELECT DISTINCT metodologia FROM Proyectos")
    metodologias = [r[0] for r in cursor.fetchall()]
    print(f"📌 Metodologías disponibles: {metodologias}")

# Verificar estados
if 'estado' in columnas_existentes:
    cursor.execute("SELECT DISTINCT estado FROM Proyectos")
    estados = [r[0] for r in cursor.fetchall()]
    print(f"📌 Estados disponibles: {estados}")

cursor.close()
conn.close()
print("\n✅ Script completado\n")
