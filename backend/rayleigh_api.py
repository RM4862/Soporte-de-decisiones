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
CORS(APP, resources={r"/*": {"origins": ["http://localhost:3001", "http://localhost:3000", "http://localhost:5173"]}})

MODEL_FILE = os.getenv('MODEL_FILE', 'rayleigh_model.json')
RESP_KEY = os.getenv('RESP_KEY', 'changeme')

# CONFIGURACIÓN DB
SG_DB = {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'SG_Proyectos'}
DSS_DB = {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'DSS_Proyectos'}

def load_model():
    if not os.path.exists(MODEL_FILE): return None
    with open(MODEL_FILE, 'r', encoding='utf-8') as f: return json.load(f)

# --- RUTAS DE PREDICCIÓN (Tu lógica original intacta) ---
@APP.route('/predict', methods=['POST'])
def predict():
    # ... (Tu código original de predicción va aquí, sin cambios) ...
    # Para ahorrar espacio en la respuesta, asumo que mantienes tu código de predicción
    # Si lo necesitas completo, avísame.
    pass 

# ... (Funciones auxiliares _build_filters_sql y predict_filtered también van aquí) ...
# Pega aquí tus funciones _build_filters_sql y predict_filtered del archivo anterior.

# --- RUTA OLAP (LA CORRECCIÓN IMPORTANTE) ---
@APP.route('/api/olap/cube', methods=['GET'])
def olap_cube():
    dimension = request.args.get('dimension', 'tiempo')
    metric = request.args.get('metric', 'cantidad')
    year_filter = request.args.get('year', 'all')
    
    try:
        conn = mysql.connector.connect(**DSS_DB)
        cursor = conn.cursor(dictionary=True)
        
        year_clause = ""
        params = []
        if year_filter != 'all':
            year_clause = " AND t.anio = %s "
            params.append(year_filter)

        # 1. TIEMPO
        if dimension == 'tiempo':
            if metric == 'defectos':
                # Conteo real desde Fact_Defectos
                query = f"""
                    SELECT CONCAT('Q', t.trimestre, '-', t.anio) as periodo,
                           CAST(COUNT(fd.id_fact_defecto) AS FLOAT) as value,
                           CAST(COUNT(DISTINCT fd.id_proyecto) AS FLOAT) as proyectos,
                           0 as ingresos
                    FROM Fact_Defectos fd
                    JOIN Dim_Tiempo t ON fd.id_tiempo = t.id_tiempo
                    WHERE 1=1 {year_clause}
                    GROUP BY t.anio, t.trimestre
                    ORDER BY t.anio, t.trimestre
                """
            else:
                metric_sql = "CAST(COUNT(fp.id_proyecto) AS FLOAT)"
                if metric == 'ingresos': metric_sql = "CAST(SUM(fp.costo_total) AS FLOAT)"
                query = f"""
                    SELECT CONCAT('Q', t.trimestre, '-', t.anio) as periodo,
                           {metric_sql} as value,
                           CAST(SUM(fp.costo_total) AS FLOAT) as ingresos,
                           CAST(COUNT(fp.id_proyecto) AS FLOAT) as proyectos
                    FROM Fact_Proyectos fp
                    JOIN Dim_Tiempo t ON fp.id_tiempo = t.id_tiempo
                    WHERE 1=1 {year_clause}
                    GROUP BY t.anio, t.trimestre
                    ORDER BY t.anio, t.trimestre
                """
        
        # 2. CLIENTE (Top 10 Pareto)
        elif dimension == 'cliente':
            metric_col = "CAST(COUNT(fp.id_proyecto) AS FLOAT)"
            if metric == 'ingresos': metric_col = "CAST(SUM(fp.costo_total) AS FLOAT)"
            
            query = f"""
                SELECT c.nombre as label,
                       {metric_col} as value,
                       CAST(COUNT(fp.id_proyecto) AS FLOAT) as proyectos,
                       CAST(SUM(fp.costo_total) AS FLOAT) as ingresos
                FROM Fact_Proyectos fp
                JOIN Dim_Cliente c ON fp.id_cliente = c.id_cliente
                JOIN Dim_Tiempo t ON fp.id_tiempo = t.id_tiempo
                WHERE 1=1 {year_clause}
                GROUP BY c.nombre
                ORDER BY value DESC
                LIMIT 15
            """
        
        # 3. ETAPA (Rayleigh)
        elif dimension == 'etapa':
             query = f"""
                SELECT fd.etapa_deteccion as etapa,
                       CAST(COUNT(*) AS FLOAT) as value,
                       CAST(COUNT(*) AS FLOAT) as cantidad_defectos,
                       0 as ingresos, 0 as proyectos
                FROM Fact_Defectos fd
                LEFT JOIN Dim_Tiempo t ON fd.id_tiempo = t.id_tiempo
                WHERE fd.etapa_deteccion IS NOT NULL {year_clause}
                GROUP BY fd.etapa_deteccion
                ORDER BY FIELD(fd.etapa_deteccion, 'Inicio', 'Planificación', 'Etapa 1', 'Etapa 2', 'Etapa 3', 'Etapa 4', 'Etapa 5', 'Ejecución', 'Cierre')
            """

        # 4. TECNOLOGIA
        elif dimension == 'tecnologia':
            metric_col = "CAST(COUNT(*) AS FLOAT)"
            if metric == 'ingresos': metric_col = "CAST(SUM(fp.costo_total) AS FLOAT)"
            query = f"""
                SELECT p.metodologia as tecnologia, 
                       {metric_col} as value,
                       CAST(COUNT(fp.id_proyecto) AS FLOAT) as proyectos,
                       CAST(SUM(fp.costo_total) AS FLOAT) as ingresos
                FROM Fact_Proyectos fp
                JOIN Dim_Proyecto p ON fp.id_proyecto = p.id_proyecto
                JOIN Dim_Tiempo t ON fp.id_tiempo = t.id_tiempo
                WHERE 1=1 {year_clause}
                GROUP BY p.metodologia
                ORDER BY value DESC
            """

        cursor.execute(query, params)
        data = cursor.fetchall()
        return jsonify(data)

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000, debug=True)