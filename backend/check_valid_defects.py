import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='SG_Proyectos'
)

cursor = conn.cursor()

# Defectos TOTALES con esos filtros
cursor.execute("""
SELECT COUNT(*) 
FROM Defectos d 
JOIN Proyectos p ON d.id_proyecto = p.id_proyecto 
WHERE p.metodologia = %s 
AND p.horas_invertidas <= %s 
AND d.fecha_deteccion IS NOT NULL 
AND p.fecha_inicio IS NOT NULL
""", ('Scrum', 553))
total = cursor.fetchone()[0]

# Defectos VÁLIDOS (fecha_deteccion >= fecha_inicio)
cursor.execute("""
SELECT COUNT(*) 
FROM Defectos d 
JOIN Proyectos p ON d.id_proyecto = p.id_proyecto 
WHERE p.metodologia = %s 
AND p.horas_invertidas <= %s 
AND d.fecha_deteccion >= p.fecha_inicio
AND d.fecha_deteccion IS NOT NULL 
AND p.fecha_inicio IS NOT NULL
""", ('Scrum', 553))
validos = cursor.fetchone()[0]

print("=" * 60)
print("ANÁLISIS DE DEFECTOS CON FILTROS:")
print(f"  Metodología: Scrum")
print(f"  Horas invertidas máximas: 553")
print("=" * 60)
print(f"\nDefectos TOTALES: {total}")
print(f"Defectos VÁLIDOS (fecha >= inicio): {validos}")
print(f"Defectos INVÁLIDOS (fecha < inicio): {total - validos}")

if validos == 0:
    print("\n❌ NO HAY DEFECTOS VÁLIDOS con esos filtros")
    print("\n💡 Solución: Usa filtros más amplios o sin filtros")
else:
    print(f"\n✅ Hay {validos} defectos válidos")

conn.close()
