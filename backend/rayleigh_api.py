import os
import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from typing import List, Tuple
from collections import defaultdict
from rayleigh_model import fit_rayleigh, expected_value, percentile

APP = Flask(__name__)
CORS(APP, resources={r"/*": {"origins": ["http://localhost:3001", "http://localhost:3000", "http://localhost:3002", "http://localhost:5173"]}})

MODEL_FILE = os.getenv('MODEL_FILE', 'rayleigh_model.json')
RESP_KEY = os.getenv('RESP_KEY', 'changeme')

# CONFIGURACIÓN DB
SG_DB = {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'SG_Proyectos'}
DSS_DB = {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'DSS_Proyectos'}

def load_model():
    if not os.path.exists(MODEL_FILE): return None
    with open(MODEL_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def _build_filters_sql(filters):
    """Construye cláusula WHERE basada en filtros del frontend"""
    where = []
    params = []
    
    if 'metodologia' in filters and filters.get('metodologia'):
        where.append('p.metodologia = %s')
        params.append(filters['metodologia'])
    
    if 'horas_invertidas_min' in filters and filters.get('horas_invertidas_min'):
        where.append('p.horas_invertidas >= %s')
        params.append(int(filters['horas_invertidas_min']))
    if 'horas_invertidas_max' in filters and filters.get('horas_invertidas_max'):
        where.append('p.horas_invertidas <= %s')
        params.append(int(filters['horas_invertidas_max']))
    
    if 'presupuesto_min' in filters and filters.get('presupuesto_min'):
        where.append('p.presupuesto >= %s')
        params.append(float(filters['presupuesto_min']))
    if 'presupuesto_max' in filters and filters.get('presupuesto_max'):
        where.append('p.presupuesto <= %s')
        params.append(float(filters['presupuesto_max']))
    
    if 'duracion_dias_min' in filters and filters.get('duracion_dias_min'):
        where.append('DATEDIFF(p.fecha_fin, p.fecha_inicio) >= %s')
        params.append(int(filters['duracion_dias_min']))
    if 'duracion_dias_max' in filters and filters.get('duracion_dias_max'):
        where.append('DATEDIFF(p.fecha_fin, p.fecha_inicio) <= %s')
        params.append(int(filters['duracion_dias_max']))
    
    if 'estado' in filters and filters.get('estado'):
        if isinstance(filters['estado'], list):
            placeholders = ','.join(['%s'] * len(filters['estado']))
            where.append(f"p.estado IN ({placeholders})")
            params.extend(filters['estado'])
        else:
            where.append('p.estado = %s')
            params.append(filters['estado'])
    
    if 'entregables_count_min' in filters and filters.get('entregables_count_min'):
        where.append('p.entregables_count >= %s')
        params.append(int(filters['entregables_count_min']))
    if 'entregables_count_max' in filters and filters.get('entregables_count_max'):
        where.append('p.entregables_count <= %s')
        params.append(int(filters['entregables_count_max']))
    
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
    """Aplica filtros desde frontend, consulta SG_Proyectos y ajusta Rayleigh dinámicamente"""
    auth = request.headers.get('Authorization') or (request.json.get('auth_key') if request.is_json else None)
    if auth is None or auth != RESP_KEY:
        abort(401, 'Unauthorized: missing or invalid auth key')
    
    filters = request.json.get('filters') if request.is_json else None
    clause, params = _build_filters_sql(filters)
    
    try:
        conn = mysql.connector.connect(**SG_DB)
        cursor = conn.cursor()
        
        query = f"""
            SELECT 
                p.id_proyecto,
                p.nombre,
                p.metodologia,
                p.fecha_inicio,
                p.fecha_fin,
                d.fecha_deteccion,
                FLOOR(DATEDIFF(d.fecha_deteccion, p.fecha_inicio) / 7) AS semana
            FROM Proyectos p
            INNER JOIN Defectos d ON p.id_proyecto = d.id_proyecto
            WHERE d.fecha_deteccion >= p.fecha_inicio
            {clause}
            ORDER BY semana
        """
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({'error': 'No matching data found with those filters'}), 404
        
        # Extraer muestras (semanas) y contar defectos por semana
        samples = [row[6] for row in rows if row[6] is not None and row[6] >= 0]
        if not samples:
            return jsonify({'error': 'No valid time samples'}), 400
        
        # Ajustar modelo Rayleigh
        sigma, n, mean_sq = fit_rayleigh(samples)
        exp_val = expected_value(sigma)
        p90 = percentile(sigma, 0.90)
        
        # Información de proyectos y metodologías
        proyectos_info = [(row[0], row[2]) for row in rows]
        proyectos_unicos = len(set([pid for pid, _ in proyectos_info]))
        metodologias_usadas = list(set([m for _, m in proyectos_info]))
        
        # Calcular duración en semanas
        max_semana = max(samples)
        duracion_semanas = max_semana + 1
        
        # Construir información detallada para el frontend con defectos acumulados
        defectos_por_semana = defaultdict(int)
        for s in samples:
            defectos_por_semana[s] += 1
        
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
        
        result = {
            'sigma': round(sigma, 2),
            'n_samples': n,
            'expected_defects': round(exp_val, 2),
            'p90': round(p90, 2),
            'proyectos_analizados': proyectos_unicos,
            'metodologias': metodologias_usadas,
            'duracion_semanas': duracion_semanas,
            'tiempo_data': tiempo_info
        }
        
        cursor.close()
        conn.close()
        return jsonify(result)
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@APP.route('/api/olap/cube', methods=['GET'])
def olap_cube():
    """Endpoint OLAP para análisis multidimensional"""
    dimension = request.args.get('dimension', 'cliente')
    metric = request.args.get('metric', 'ingresos')
    year = request.args.get('year', 'all')
    
    try:
        # Usar siempre SG_Proyectos
        conn = mysql.connector.connect(**SG_DB)
        cursor = conn.cursor(dictionary=True)
        
        # Construir query según dimensión
        if dimension == 'cliente':
            query = """
                SELECT 
                    p.cliente as label,
                    COUNT(p.id_proyecto) as proyectos,
                    COALESCE(SUM(p.presupuesto), 0) as ingresos,
                    COALESCE(SUM(p.presupuesto), 0) as value,
                    COUNT(d.id_defecto) as defectos
                FROM Proyectos p
                LEFT JOIN Defectos d ON p.id_proyecto = d.id_proyecto
            """
            where_clause = f" WHERE YEAR(p.fecha_inicio) = {year}" if year != 'all' else ""
            query += where_clause + " GROUP BY p.cliente ORDER BY ingresos DESC"
            
        elif dimension == 'tiempo':
            query = """
                SELECT 
                    DATE_FORMAT(p.fecha_inicio, '%Y-%m') as periodo,
                    COUNT(p.id_proyecto) as proyectos,
                    COALESCE(SUM(p.presupuesto), 0) as ingresos,
                    COALESCE(SUM(p.presupuesto), 0) as value,
                    COUNT(d.id_defecto) as defectos
                FROM Proyectos p
                LEFT JOIN Defectos d ON p.id_proyecto = d.id_proyecto
            """
            where_clause = f" WHERE YEAR(p.fecha_inicio) = {year}" if year != 'all' else ""
            query += where_clause + " GROUP BY DATE_FORMAT(p.fecha_inicio, '%Y-%m') ORDER BY periodo"
            
        elif dimension == 'etapa':
            query = """
                SELECT 
                    COALESCE(d.etapa_deteccion, 'Sin etapa') as etapa,
                    COUNT(DISTINCT p.id_proyecto) as proyectos,
                    COALESCE(SUM(p.presupuesto), 0) as ingresos,
                    COUNT(d.id_defecto) as defectos,
                    COUNT(d.id_defecto) as value
                FROM Defectos d
                INNER JOIN Proyectos p ON d.id_proyecto = p.id_proyecto
            """
            where_clause = f" WHERE YEAR(p.fecha_inicio) = {year}" if year != 'all' else ""
            query += where_clause + " GROUP BY d.etapa_deteccion ORDER BY defectos DESC"
            
        elif dimension == 'tecnologia':
            query = """
                SELECT 
                    p.metodologia as tecnologia,
                    COUNT(p.id_proyecto) as proyectos,
                    COALESCE(SUM(p.presupuesto), 0) as ingresos,
                    COALESCE(SUM(p.presupuesto), 0) as value,
                    COUNT(d.id_defecto) as defectos
                FROM Proyectos p
                LEFT JOIN Defectos d ON p.id_proyecto = d.id_proyecto
            """
            where_clause = f" WHERE YEAR(p.fecha_inicio) = {year}" if year != 'all' else ""
            query += where_clause + " GROUP BY p.metodologia ORDER BY proyectos DESC"
        else:
            return jsonify({'error': 'Invalid dimension'}), 400
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Ajustar métrica si es necesario
        if metric == 'cantidad':
            for row in results:
                row['value'] = row['proyectos']
        elif metric == 'defectos':
            for row in results:
                row['value'] = row.get('defectos', 0)
        
        cursor.close()
        conn.close()
        
        return jsonify(results if results else [])
        
    except Error as e:
        return jsonify({'error': str(e), 'message': 'Database connection or query failed'}), 500

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000, debug=True)
