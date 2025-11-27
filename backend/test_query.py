import mysql.connector

# Simular la query que hace el backend
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='SG_Proyectos'
)

cursor = conn.cursor()

# Query exacta que hace el backend con los filtros
filters = {
    'metodologia': 'Scrum',
    'horas_invertidas_max': 553
}

query = """
    SELECT 
        FLOOR(DATEDIFF(d.fecha_deteccion, p.fecha_inicio) / 7) as semana_deteccion,
        COUNT(*) as num_defectos
    FROM Defectos d
    JOIN Proyectos p ON d.id_proyecto = p.id_proyecto
    WHERE p.fecha_inicio IS NOT NULL
      AND d.fecha_deteccion IS NOT NULL
"""

params = []
where_conditions = []

if 'metodologia' in filters and filters.get('metodologia'):
    where_conditions.append('p.metodologia = %s')
    params.append(filters['metodologia'])

if 'horas_invertidas_max' in filters and filters.get('horas_invertidas_max'):
    where_conditions.append('p.horas_invertidas <= %s')
    params.append(int(filters['horas_invertidas_max']))

if where_conditions:
    query += " AND " + " AND ".join(where_conditions)

query += """
    GROUP BY semana_deteccion
    ORDER BY semana_deteccion
"""

print("Query que se ejecutará:")
print(query)
print(f"\nParámetros: {params}")
print("=" * 60)

cursor.execute(query, params)
results = cursor.fetchall()

print(f"\nResultados encontrados: {len(results)} semanas con defectos")

if results:
    print("\nPrimeras 10 semanas:")
    for row in results[:10]:
        print(f"  Semana {row[0]}: {row[1]} defectos")
    
    total_defectos = sum(row[1] for row in results)
    print(f"\nTotal defectos: {total_defectos}")
else:
    print("\n❌ NO SE ENCONTRARON DATOS")
    print("\nVerificando por qué...")
    
    # Verificar proyectos que cumplen los filtros
    cursor.execute("""
        SELECT id_proyecto, nombre, metodologia, horas_invertidas, fecha_inicio
        FROM Proyectos
        WHERE metodologia = %s AND horas_invertidas <= %s
    """, (filters['metodologia'], filters['horas_invertidas_max']))
    
    proyectos = cursor.fetchall()
    print(f"\nProyectos que cumplen los filtros: {len(proyectos)}")
    for p in proyectos:
        print(f"  ID {p[0]}: {p[1]} - {p[3]} horas - Inicio: {p[4]}")
    
    if proyectos:
        # Verificar defectos de esos proyectos
        ids = [p[0] for p in proyectos]
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(f"""
            SELECT id_proyecto, COUNT(*) as num_defectos
            FROM Defectos
            WHERE id_proyecto IN ({placeholders})
            AND fecha_deteccion IS NOT NULL
            GROUP BY id_proyecto
        """, ids)
        
        defectos = cursor.fetchall()
        print(f"\nDefectos por proyecto:")
        for d in defectos:
            print(f"  Proyecto {d[0]}: {d[1]} defectos")

conn.close()
