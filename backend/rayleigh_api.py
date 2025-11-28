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
SG_DB = {
    'host': os.getenv('SG_HOST', 'localhost'),
    'user': os.getenv('SG_USER', 'root'),
    'password': os.getenv('SG_PASSWORD', ''),
    'database': os.getenv('SG_DATABASE', 'SG_Proyectos')
}
DSS_DB = {
    'host': os.getenv('DW_HOST', 'localhost'),
    'user': os.getenv('DW_USER', 'root'),
    'password': os.getenv('DW_PASSWORD', ''),
    'database': os.getenv('DW_DATABASE', 'DSS_Proyectos')
}

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

@APP.route('/api/dashboard/summary', methods=['GET'])
def dashboard_summary():
    """Endpoint para datos del dashboard principal"""
    try:
        conn = mysql.connector.connect(**SG_DB)
        cursor = conn.cursor(dictionary=True)
        
        # KPI 1: Proyectos Activos
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM Proyectos 
            WHERE estado IN ('En Desarrollo', 'Testing', 'En Progreso')
        """)
        proyectos_activos = cursor.fetchone()['total']
        
        # Cambio vs mes anterior
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Proyectos
            WHERE estado IN ('En Desarrollo', 'Testing', 'En Progreso')
            AND fecha_inicio >= DATE_SUB(CURDATE(), INTERVAL 2 MONTH)
            AND fecha_inicio < DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        """)
        proyectos_mes_anterior = cursor.fetchone()['total'] or 1
        cambio_proyectos = round(((proyectos_activos - proyectos_mes_anterior) / proyectos_mes_anterior) * 100)
        
        # KPI 2: Ingresos del mes actual
        cursor.execute("""
            SELECT COALESCE(SUM(presupuesto), 0) as total
            FROM Proyectos
            WHERE YEAR(fecha_inicio) = YEAR(CURDATE())
            AND MONTH(fecha_inicio) = MONTH(CURDATE())
        """)
        ingresos = cursor.fetchone()['total']
        
        # Cambio ingresos vs mes anterior
        cursor.execute("""
            SELECT COALESCE(SUM(presupuesto), 0) as total
            FROM Proyectos
            WHERE fecha_inicio >= DATE_SUB(CURDATE(), INTERVAL 2 MONTH)
            AND fecha_inicio < DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        """)
        ingresos_anterior = cursor.fetchone()['total'] or 1
        cambio_ingresos = round(((ingresos - ingresos_anterior) / ingresos_anterior) * 100)
        
        # KPI 3: Satisfacción promedio
        cursor.execute("""
            SELECT COALESCE(AVG(calificacion), 4.2) as promedio
            FROM evaluaciones_cliente
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
        """)
        satisfaccion = cursor.fetchone()['promedio']
        
        # KPI 4: Defectos críticos activos
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Defectos
            WHERE severidad = 'Crítico'
            AND estado = 'Abierto'
        """)
        defectos_criticos = cursor.fetchone()['total']
        
        # Cambio defectos
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Defectos
            WHERE severidad = 'Crítico'
            AND fecha_deteccion >= DATE_SUB(CURDATE(), INTERVAL 2 MONTH)
            AND fecha_deteccion < DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        """)
        defectos_anterior = cursor.fetchone()['total'] or 1
        cambio_defectos = round(((defectos_criticos - defectos_anterior) / defectos_anterior) * 100)
        
        # Proyectos por mes (últimos 6 meses)
        cursor.execute("""
            SELECT 
                DATE_FORMAT(fecha_inicio, '%b') as name,
                COUNT(*) as proyectos,
                SUM(CASE WHEN estado = 'Completado' THEN 1 ELSE 0 END) as completados
            FROM Proyectos
            WHERE fecha_inicio >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY YEAR(fecha_inicio), MONTH(fecha_inicio)
            ORDER BY fecha_inicio
        """)
        proyectos_mes = cursor.fetchall()
        
        # Defectos por severidad (activos)
        cursor.execute("""
            SELECT 
                severidad as name,
                COUNT(*) as value,
                CASE severidad
                    WHEN 'Crítico' THEN '#ef4444'
                    WHEN 'Mayor' THEN '#f59e0b'
                    WHEN 'Menor' THEN '#10b981'
                    WHEN 'Cosmético' THEN '#6366f1'
                END as color
            FROM Defectos
            WHERE estado = 'Abierto'
            GROUP BY severidad
            ORDER BY 
                CASE severidad
                    WHEN 'Crítico' THEN 1
                    WHEN 'Mayor' THEN 2
                    WHEN 'Menor' THEN 3
                    WHEN 'Cosmético' THEN 4
                END
        """)
        defectos_severidad = cursor.fetchall()
        
        # Proyectos recientes (últimos 5)
        cursor.execute("""
            SELECT 
                p.nombre as proyecto,
                c.nombre as cliente,
                p.estado,
                CASE 
                    WHEN p.fecha_fin IS NULL OR p.fecha_inicio IS NULL THEN 0
                    WHEN DATEDIFF(p.fecha_fin, p.fecha_inicio) = 0 THEN 100
                    ELSE LEAST(100, GREATEST(0, ROUND((DATEDIFF(CURDATE(), p.fecha_inicio) / 
                           DATEDIFF(p.fecha_fin, p.fecha_inicio)) * 100)))
                END as progreso
            FROM Proyectos p
            LEFT JOIN Clientes c ON p.id_cliente = c.id_cliente
            ORDER BY p.fecha_inicio DESC
            LIMIT 5
        """)
        proyectos_recientes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'kpis': {
                'proyectos_activos': {
                    'value': proyectos_activos,
                    'change': cambio_proyectos,
                    'trend': 'up' if cambio_proyectos >= 0 else 'down'
                },
                'ingresos_mensuales': {
                    'value': ingresos,
                    'change': cambio_ingresos,
                    'trend': 'up' if cambio_ingresos >= 0 else 'down'
                },
                'satisfaccion': {
                    'value': round(satisfaccion, 1),
                    'change': 5,  # Placeholder, podrías calcular vs periodo anterior
                    'trend': 'up'
                },
                'defectos_criticos': {
                    'value': defectos_criticos,
                    'change': cambio_defectos,
                    'trend': 'down' if cambio_defectos <= 0 else 'up'
                }
            },
            'proyectos_mes': proyectos_mes,
            'defectos_severidad': defectos_severidad,
            'proyectos_recientes': proyectos_recientes
        })
        
    except Error as e:
        return jsonify({'error': str(e), 'message': 'Database query failed'}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask server on port 5000...")
    try:
        APP.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
