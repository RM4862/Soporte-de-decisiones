"""
train_rayleigh.py
------------------
Script para entrenar el modelo Rayleigh usando el historial de incidencias
almacenado en `SG_Proyectos.Incidencias`. El script realiza:

- Conexión a la base de datos de gestión (`SG_Proyectos`).
- Consulta: conteo de incidencias por proyecto (`GROUP BY id_proyecto`).
- Ajuste de sigma (MLE) usando `rayleigh_model.fit_rayleigh`.
- Guarda el modelo en `rayleigh_model.json`.
- Opcionalmente persiste los parámetros (sigma, n_samples, mean_sq)
    en la tabla `Model_Rayleigh` del Data Warehouse para trazabilidad.

La configuración se puede pasar por variables de entorno (ver `README.md`).
"""
import os
import json
from datetime import datetime
import mysql.connector
from rayleigh_model import fit_rayleigh, expected_value, percentile

# Config via environment variables for safety (defaults provided for dev)
SG_DB = {
    'host': os.getenv('SG_HOST', 'localhost'),
    'user': os.getenv('SG_USER', 'root'),
    'password': os.getenv('SG_PASSWORD', ''),
    'database': os.getenv('SG_DATABASE', 'SG_Proyectos')
}

# DW connection to persist model (optional)
DW_DB = {
    'host': os.getenv('DW_HOST', 'localhost'),
    'user': os.getenv('DW_USER', 'root'),
    'password': os.getenv('DW_PASSWORD', ''),
    'database': os.getenv('DW_DATABASE', 'DSS_Proyectos')
}

MODEL_FILE = os.getenv('MODEL_FILE', 'rayleigh_model.json')

def fetch_defect_counts(conn):
    """Extrae el conteo de defectos usando tiempo calendario normalizado.

    Calcula semanas transcurridas desde el inicio del proyecto hasta la detección
    del defecto. Esto funciona para CUALQUIER metodología (Scrum, Waterfall, 
    Kanban, RUP, XP, DevOps) sin importar sus fases específicas.
    
    Retorna defectos agrupados por intervalos de tiempo (semanas).
    """
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
    ORDER BY 
        p.id_proyecto, semana_deteccion
    """
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    
    if len(rows) == 0:
        return []
    
    # Agrupar defectos por semana (tiempo normalizado)
    # Esto crea un histograma de defectos por unidad de tiempo
    from collections import defaultdict
    defectos_por_semana = defaultdict(int)
    
    for row in rows:
        semana = int(row[6]) if row[6] is not None and row[6] >= 0 else 0
        defectos_por_semana[semana] += 1
    
    # Convertir a lista ordenada de conteos
    # Incluir semanas sin defectos (0s) para tener serie completa
    if defectos_por_semana:
        max_semana = max(defectos_por_semana.keys())
        samples = [defectos_por_semana.get(i, 0) for i in range(max_semana + 1)]
    else:
        samples = []
    
    return samples


def persist_model_to_dw(dw_conn, sigma, n, mean_sq):
    """Persiste los parámetros del modelo en `DSS_Proyectos.Model_Rayleigh`.

    Nota: asume que la tabla ya existe (se añadió al DDL del DW).
    """
    cur = dw_conn.cursor()
    sql = "INSERT INTO Model_Rayleigh (sigma, n_samples, mean_sq, trained_at, notes) VALUES (%s,%s,%s,%s,%s)"
    notes = 'Entrenado desde SG_Proyectos.Defectos usando tiempo calendario (semanas) - Compatible con todas las metodologías'
    cur.execute(sql, (float(sigma), int(n), float(mean_sq), datetime.now(), notes))
    dw_conn.commit()
    cur.close()


def main(persist_to_dw=True):
    # 1) Conectar a SG y extraer conteos por tiempo (semanas)
    print("Conectando a SG_Proyectos para obtener defectos por tiempo calendario...")
    sg = mysql.connector.connect(**SG_DB)
    samples = fetch_defect_counts(sg)
    sg.close()

    print(f"Muestras obtenidas: {len(samples)} períodos de tiempo (semanas)")
    print(f"Distribución de defectos: {samples}")
    if len(samples) == 0:
        print("No hay datos para entrenar.")
        return

    # 2) Ajustar el modelo Rayleigh usando las muestras extraídas
    sigma, n, mean_sq = fit_rayleigh(samples)
    expected = expected_value(sigma)
    p90 = percentile(sigma, 0.9)

    model = {
        'sigma': sigma,
        'n_samples': n,
        'mean_sq': mean_sq,
        'expected': expected,
        'p90': p90,
        'trained_at': datetime.now().isoformat()
    }

    # 3) Guardar localmente el modelo en formato JSON
    with open(MODEL_FILE, 'w', encoding='utf-8') as f:
        json.dump(model, f, indent=2)

    print(f"Modelo guardado en {MODEL_FILE}")

    # 4) Persistir en DW (opcional) para trazabilidad/versionado
    if persist_to_dw:
        print("Persistiendo parámetros en DW (Model_Rayleigh)...")
        dw = mysql.connector.connect(**DW_DB)
        persist_model_to_dw(dw, sigma, n, mean_sq)
        dw.close()
        print("Persistencia en DW completada.")

    print("Resumen del modelo:")
    print(json.dumps(model, indent=2))


if __name__ == '__main__':
    main(persist_to_dw=True)
