import mysql.connector
from rayleigh_model import fit_rayleigh, expected_value, percentile

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='SG_Proyectos'
)

cursor = conn.cursor()

# Simular exactamente lo que hace el backend
print("=" * 60)
print("SIMULANDO BACKEND CON FILTROS:")
print("  Metodología: Scrum")
print("  Horas invertidas máximas: 2000")
print("=" * 60)

query = """
SELECT 
    p.id_proyecto,
    p.metodologia,
    p.fecha_inicio,
    p.fecha_fin,
    DATEDIFF(p.fecha_fin, p.fecha_inicio) as duracion_dias,
    d.fecha_deteccion,
    FLOOR(DATEDIFF(d.fecha_deteccion, p.fecha_inicio) / 7) as semana_deteccion
FROM 
    Defectos d
JOIN 
    Proyectos p ON d.id_proyecto = p.id_proyecto
WHERE 
    d.fecha_deteccion IS NOT NULL
    AND p.fecha_inicio IS NOT NULL
    AND d.fecha_deteccion >= p.fecha_inicio
    AND p.metodologia = %s
    AND p.horas_invertidas <= %s
ORDER BY 
    p.id_proyecto, semana_deteccion
"""

cursor.execute(query, ('Scrum', 2000))
rows = cursor.fetchall()

print(f"\n✅ Filas obtenidas: {len(rows)}")

if len(rows) == 0:
    print("\n❌ NO HAY DATOS - El backend retornaría error 400")
else:
    # Procesar igual que el backend
    from collections import defaultdict
    defectos_por_semana = defaultdict(int)
    proyectos_info = set()
    
    for row in rows:
        semana = int(row[6]) if row[6] is not None and row[6] >= 0 else 0
        defectos_por_semana[semana] += 1
        proyectos_info.add((row[0], row[1]))
    
    print(f"\n📊 Proyectos únicos analizados: {len(proyectos_info)}")
    print(f"📊 Semanas con defectos: {len(defectos_por_semana)}")
    
    if defectos_por_semana:
        max_semana = max(defectos_por_semana.keys())
        samples = [defectos_por_semana.get(i, 0) for i in range(max_semana + 1)]
        
        print(f"📊 Semana máxima: {max_semana}")
        print(f"📊 Total muestras para Rayleigh: {len(samples)}")
        print(f"📊 Total defectos: {sum(samples)}")
        
        # Fit Rayleigh
        try:
            sigma, n, mean_sq = fit_rayleigh(samples)
            exp_defects = expected_value(sigma)
            p90 = percentile(sigma, 0.90)
            p95 = percentile(sigma, 0.95)
            
            print(f"\n✅ MODELO RAYLEIGH AJUSTADO:")
            print(f"   σ (sigma) = {sigma:.2f}")
            print(f"   Muestras = {n}")
            print(f"   Defectos esperados/semana = {exp_defects:.2f}")
            print(f"   P90 = {p90:.2f}")
            print(f"   P95 = {p95:.2f}")
            
            # Construir tiempo_data como lo hace el backend
            tiempo_data = []
            cumulative = 0
            for semana in range(max_semana + 1):
                defectos = defectos_por_semana.get(semana, 0)
                cumulative += defectos
                tiempo_data.append({
                    'tiempo': semana,
                    'defectos_esperados': defectos,
                    'defectos_acumulados': cumulative
                })
            
            print(f"\n✅ tiempo_data generado con {len(tiempo_data)} elementos")
            print(f"   Primeras 5 semanas:")
            for item in tiempo_data[:5]:
                print(f"     Semana {item['tiempo']}: {item['defectos_esperados']} defectos, {item['defectos_acumulados']} acumulados")
            
            print("\n🎯 EL BACKEND DEBERÍA RETORNAR DATOS CORRECTAMENTE")
            
        except Exception as e:
            print(f"\n❌ ERROR al ajustar Rayleigh: {e}")
    else:
        print("\n❌ No hay defectos por semana")

conn.close()
