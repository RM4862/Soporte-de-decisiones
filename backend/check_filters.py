import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='SG_Proyectos'
)

cursor = conn.cursor()

# Verificar proyectos Scrum
print("=" * 60)
print("ANÁLISIS DE PROYECTOS SCRUM")
print("=" * 60)

cursor.execute("""
    SELECT 
        id_proyecto,
        nombre,
        metodologia,
        horas_invertidas,
        DATEDIFF(fecha_fin, fecha_inicio) as duracion_dias,
        presupuesto,
        estado
    FROM Proyectos 
    WHERE metodologia = 'Scrum'
    ORDER BY horas_invertidas
""")

proyectos = cursor.fetchall()
print(f"\nTotal proyectos Scrum: {len(proyectos)}\n")

if proyectos:
    print(f"{'ID':<5} {'Nombre':<30} {'Horas':<10} {'Días':<10} {'Presupuesto':<15} {'Estado':<15}")
    print("-" * 100)
    for p in proyectos[:10]:  # Mostrar solo los primeros 10
        print(f"{p[0]:<5} {p[1][:28]:<30} {p[3]:<10} {p[4]:<10} {p[5]:<15} {p[6]:<15}")
    
    if len(proyectos) > 10:
        print(f"\n... y {len(proyectos) - 10} proyectos más")

# Rangos de horas invertidas
cursor.execute("""
    SELECT 
        MIN(horas_invertidas) as min_horas,
        MAX(horas_invertidas) as max_horas,
        AVG(horas_invertidas) as promedio_horas
    FROM Proyectos 
    WHERE metodologia = 'Scrum'
""")
stats = cursor.fetchone()
print(f"\nEstadísticas de horas invertidas en Scrum:")
print(f"  Mínimo: {stats[0]} horas")
print(f"  Máximo: {stats[1]} horas")
print(f"  Promedio: {stats[2]:.2f} horas")

# Verificar con filtro específico horas_invertidas_max <= 553
cursor.execute("""
    SELECT COUNT(*) 
    FROM Proyectos 
    WHERE metodologia = 'Scrum' 
    AND horas_invertidas <= 553
""")
count = cursor.fetchone()[0]
print(f"\nProyectos Scrum con horas_invertidas <= 553: {count}")

# Verificar defectos disponibles
cursor.execute("""
    SELECT COUNT(DISTINCT p.id_proyecto) as proyectos_con_defectos
    FROM Proyectos p
    JOIN Defectos d ON p.id_proyecto = d.id_proyecto
    WHERE p.metodologia = 'Scrum'
    AND p.fecha_inicio IS NOT NULL
    AND d.fecha_deteccion IS NOT NULL
""")
with_defects = cursor.fetchone()[0]
print(f"Proyectos Scrum con defectos rastreables: {with_defects}")

conn.close()
