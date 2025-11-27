"""
rayleigh_api.py
--------------
Servidor API que expone la funcionalidad de predicción Rayleigh a los
responsables de proyecto. Se ofrecen dos endpoints:

- POST /predict : devuelve la predicción basada en el último modelo entrenado.
- POST /predict_filtered : acepta filtros desde el frontend, consulta la BD
    de gestión (`SG_Proyectos`) para obtener los proyectos que cumplen los
    filtros y ajusta Rayleigh dinámicamente sobre la muestra resultante.

Autenticación: clave compartida `RESP_KEY` (en producción usar HTTPS y un
mecanismo más robusto de autenticación/autorización).
"""

import os
import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import mysql.connector
from typing import List

from rayleigh_model import fit_rayleigh, expected_value, percentile

APP = Flask(__name__)
# Configurar CORS para permitir peticiones desde el frontend
CORS(APP, resources={r"/*": {"origins": ["http://localhost:3001", "http://localhost:3000", "http://localhost:5173"]}})
MODEL_FILE = os.getenv('MODEL_FILE', 'rayleigh_model.json')
# Simple shared secret for responsables (set as env var RESPONSABLE_KEY)
RESP_KEY = os.getenv('RESP_KEY', 'changeme')

# SG DB config for on-the-fly queries (can be overridden by env vars)
SG_DB = {
    'host': os.getenv('SG_HOST', 'localhost'),
    'user': os.getenv('SG_USER', 'root'),
    'password': os.getenv('SG_PASSWORD', ''),
    'database': os.getenv('SG_DATABASE', 'SG_Proyectos')
}

# El modelo ahora usa tiempo calendario (semanas) en lugar de etapas nominales
# Esto permite funcionar con CUALQUIER metodología:
# - Scrum (sprints iterativos)
# - Waterfall (fases secuenciales)
# - Kanban (flujo continuo)
# - RUP (inception, elaboration, construction, transition)
# - XP (releases e iteraciones cortas)
# - DevOps (CI/CD continuo)


def load_model():
    """Carga el último modelo entrenado desde disco (archivo JSON)."""
    if not os.path.exists(MODEL_FILE):
        return None
    with open(MODEL_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


@APP.route('/predict', methods=['POST'])
def predict():
    """Devuelve la predicción basada en el modelo almacenado.

    Espera JSON con `auth_key` o el header `Authorization`. Opcionalmente
    acepta `round` para redondear los resultados numéricos.
    """
    auth = request.headers.get('Authorization') or (request.json.get('auth_key') if request.is_json else None)
    if auth is None or auth != RESP_KEY:
        abort(401, 'Unauthorized: missing or invalid auth key')

    model = load_model()
    if not model:
        return jsonify({'error': 'Model not found. Train model first.'}), 400

    # Return expectation and percentiles. Optionally accept rounding
    round_to = int(request.json.get('round', 0)) if request.is_json else 0
    resp = {
        'sigma': model['sigma'],
        'n_samples': model['n_samples'],
        'expected_defects': round(model['expected'], round_to),
        'p90': round(model['p90'], round_to),
        'trained_at': model.get('trained_at')
    }
    return jsonify(resp)


def _build_filters_sql(filters: dict) -> (str, List):
    """Construye la cláusula WHERE y los parámetros a partir de los filtros.

    Filtros basados en características del proyecto (agnóstico a metodología):
    - metodologia, horas_invertidas, presupuesto, duracion, estado, etc.
    
    El tiempo se calcula dinámicamente desde fecha_inicio, funcionando para
    cualquier metodología (Scrum, Waterfall, Kanban, RUP, XP, DevOps).
    """
    where = []
    params: List = []

    if filters is None:
        return "", params

    # Filtro por metodología del proyecto
    if 'metodologia' in filters and filters.get('metodologia'):
        where.append('p.metodologia = %s')
        params.append(filters['metodologia'])

    # Filtro por horas invertidas (rango)
    if 'horas_invertidas_min' in filters and filters.get('horas_invertidas_min'):
        where.append('p.horas_invertidas >= %s')
        params.append(int(filters['horas_invertidas_min']))
    if 'horas_invertidas_max' in filters and filters.get('horas_invertidas_max'):
        where.append('p.horas_invertidas <= %s')
        params.append(int(filters['horas_invertidas_max']))

    # Filtro por presupuesto (rango)
    if 'presupuesto_min' in filters and filters.get('presupuesto_min'):
        where.append('p.presupuesto >= %s')
        params.append(float(filters['presupuesto_min']))
    if 'presupuesto_max' in filters and filters.get('presupuesto_max'):
        where.append('p.presupuesto <= %s')
        params.append(float(filters['presupuesto_max']))

    # Filtro por duración del proyecto (días)
    if 'duracion_dias_min' in filters and filters.get('duracion_dias_min'):
        where.append('DATEDIFF(p.fecha_fin, p.fecha_inicio) >= %s')
        params.append(int(filters['duracion_dias_min']))
    if 'duracion_dias_max' in filters and filters.get('duracion_dias_max'):
        where.append('DATEDIFF(p.fecha_fin, p.fecha_inicio) <= %s')
        params.append(int(filters['duracion_dias_max']))

    # Filtro por estado del proyecto
    if 'estado' in filters and filters.get('estado'):
        if isinstance(filters['estado'], list):
            placeholders = ','.join(['%s'] * len(filters['estado']))
            where.append(f"p.estado IN ({placeholders})")
            params.extend(filters['estado'])
        else:
            where.append('p.estado = %s')
            params.append(filters['estado'])

    # Filtro por número de entregables
    if 'entregables_count_min' in filters and filters.get('entregables_count_min'):
        where.append('p.entregables_count >= %s')
        params.append(int(filters['entregables_count_min']))
    if 'entregables_count_max' in filters and filters.get('entregables_count_max'):
        where.append('p.entregables_count <= %s')
        params.append(int(filters['entregables_count_max']))

    # Filtro por tecnologías emergentes
    if 'num_tecnologias_emergentes_min' in filters and filters.get('num_tecnologias_emergentes_min'):
        where.append('p.num_tecnologias_emergentes >= %s')
        params.append(int(filters['num_tecnologias_emergentes_min']))
    if 'num_tecnologias_emergentes_max' in filters and filters.get('num_tecnologias_emergentes_max'):
        where.append('p.num_tecnologias_emergentes <= %s')
        params.append(int(filters['num_tecnologias_emergentes_max']))

    clause = ('AND ' + ' AND '.join(where)) if where else ''
    return clause, params


@APP.route('/predict_filtered', methods=['POST'])
def predict_filtered():
    """Apply filters from frontend, query SG_Proyectos and fit Rayleigh.

    Usa tiempo calendario (semanas desde inicio del proyecto) en lugar de
    etapas nominales. Esto permite funcionar con CUALQUIER metodología:
    Scrum, Waterfall, Kanban, RUP, XP, DevOps, etc.
    """
    auth = request.headers.get('Authorization') or (request.json.get('auth_key') if request.is_json else None)
    if auth is None or auth != RESP_KEY:
        abort(401, 'Unauthorized: missing or invalid auth key')

    filters = request.json.get('filters') if request.is_json else None

    clause, params = _build_filters_sql(filters)

    # Query que calcula semanas desde inicio del proyecto hasta detección
    # Funciona para cualquier metodología
    query = f"""
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
        {clause}
    ORDER BY 
        p.id_proyecto, semana_deteccion
    """

    # Connect to SG DB and run query
    conn = mysql.connector.connect(**SG_DB)
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if len(rows) == 0:
        return jsonify({'error': 'No matching data found for the given filters.'}), 400

    # Build samples list (defects per week)
    from collections import defaultdict
    defectos_por_semana = defaultdict(int)
    proyectos_info = set()
    
    for row in rows:
        semana = int(row[6]) if row[6] is not None and row[6] >= 0 else 0
        defectos_por_semana[semana] += 1
        proyectos_info.add((row[0], row[1]))  # (id_proyecto, metodologia)
    
    # Convertir a lista ordenada con semanas completas
    if defectos_por_semana:
        max_semana = max(defectos_por_semana.keys())
        samples = [defectos_por_semana.get(i, 0) for i in range(max_semana + 1)]
    else:
        samples = []
    
    # Fit Rayleigh on the filtered sample
    sigma, n, mean_sq = fit_rayleigh(samples)
    
    # Construir información detallada para el frontend con defectos acumulados
    tiempo_info = []
    defectos_acumulados = 0
    for i in range(max_semana + 1):
        defectos_en_semana = defectos_por_semana.get(i, 0)
        defectos_acumulados += defectos_en_semana
        tiempo_info.append({
            'tiempo': i,
            'defectos_esperados': defectos_en_semana,
            'defectos_acumulados': defectos_acumulados
        })
    
    metodologias_usadas = list(set([m for _, m in proyectos_info]))
    
    resp = {
        'sigma': sigma,
        'n_samples': n,
        'mean_sq': mean_sq,
        'expected_defects': expected_value(sigma),
        'p90': percentile(sigma, 0.9),
        'p95': percentile(sigma, 0.95),
        'tiempo_data': tiempo_info,
        'proyectos_analizados': len(proyectos_info),
        'metodologias': metodologias_usadas,
        'duracion_semanas': max_semana + 1,
        'note': 'Modelo usa tiempo calendario (semanas) - Compatible con todas las metodologías (Scrum, Waterfall, Kanban, RUP, XP, DevOps)'
    }
    return jsonify(resp)


if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    APP.run(host='0.0.0.0', port=port)
