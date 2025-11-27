import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='SG_Proyectos'
)

cursor = conn.cursor()

# Verificar columnas
cursor.execute('DESCRIBE Proyectos')
print('Columnas de Proyectos:')
for col in cursor.fetchall():
    print(f'  {col[0]} - {col[1]}')

# Verificar metodologías
cursor.execute('SELECT metodologia, COUNT(*) FROM Proyectos GROUP BY metodologia')
print('\nMetodologías disponibles:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]} proyectos')

# Verificar proyectos Scrum
cursor.execute("SELECT COUNT(*) FROM Proyectos WHERE metodologia='Scrum'")
print(f'\nTotal proyectos Scrum: {cursor.fetchone()[0]}')

# Verificar defectos con datos de tiempo
cursor.execute("""
    SELECT COUNT(DISTINCT p.id_proyecto) as proyectos, COUNT(*) as defectos
    FROM Proyectos p
    JOIN Defectos d ON p.id_proyecto = d.id_proyecto
    WHERE p.metodologia = 'Scrum'
    AND p.fecha_inicio IS NOT NULL
    AND d.fecha_deteccion IS NOT NULL
""")
result = cursor.fetchone()
print(f'\nProyectos Scrum con defectos rastreables: {result[0]} proyectos, {result[1]} defectos')

conn.close()
