# Documentación de Procesos - Sistema de Soporte de Decisión

## 📚 Índice
1. [Proceso ETL](#proceso-etl)
2. [Cubo OLAP - Especificaciones](#cubo-olap)
3. [Modelo Predictivo - Distribución de Rayleigh](#modelo-predictivo)
4. [Modelo de Madurez CMMI](#modelo-de-madurez)
5. [Procedimientos de Operación](#procedimientos)

---

## 🔄 Proceso ETL

### Visión General
El proceso ETL (Extract, Transform, Load) es fundamental para alimentar el Sistema de Soporte de Decisión con datos precisos y actualizados del sistema de gestión de proyectos.

### 1. Extracción (Extract)

#### Fuentes de Datos
1. **Sistema de Gestión de Proyectos**
   - Base de datos relacional (PostgreSQL/MySQL)
   - Tablas: proyectos, tareas, recursos, clientes
   - Frecuencia: Cada 6 horas

2. **Sistema de Control de Versiones (Git)**
   - API de GitHub/GitLab/Bitbucket
   - Métricas: commits, pull requests, líneas de código
   - Frecuencia: Diaria

3. **Sistema de Tracking de Defectos (Jira/Bugzilla)**
   - API REST
   - Datos: defectos, severidad, estado, tiempo de resolución
   - Frecuencia: Cada 2 horas

4. **Sistema de Time Tracking**
   - Base de datos de horas trabajadas
   - Datos: horas por proyecto, por tecnología, por desarrollador
   - Frecuencia: Diaria

5. **Sistema CRM (Gestión de Clientes)**
   - API del CRM
   - Datos: satisfacción, NPS, contratos, facturación
   - Frecuencia: Diaria

#### Método de Extracción
```python
# Ejemplo de extracción con Python
import psycopg2
import requests
from datetime import datetime

def extract_project_data():
    """
    Extrae datos de proyectos del sistema de gestión
    """
    conn = psycopg2.connect(
        host="db-server.company.com",
        database="project_management",
        user="etl_user",
        password="secure_password"
    )
    
    cursor = conn.cursor()
    query = """
        SELECT 
            p.id,
            p.name,
            p.start_date,
            p.end_date,
            p.budget,
            p.client_id,
            c.name as client_name,
            c.segment,
            COUNT(t.id) as total_tasks,
            COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks
        FROM projects p
        JOIN clients c ON p.client_id = c.id
        LEFT JOIN tasks t ON p.id = t.project_id
        WHERE p.last_updated >= %s
        GROUP BY p.id, c.id
    """
    
    cursor.execute(query, (last_extraction_timestamp,))
    return cursor.fetchall()

def extract_git_metrics(repo_url, token):
    """
    Extrae métricas de Git via API
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{repo_url}/api/v4/projects/statistics", headers=headers)
    return response.json()

def extract_defects():
    """
    Extrae defectos del sistema de tracking
    """
    jira_url = "https://company.atlassian.net"
    jql = "project = PROJ AND updated >= -7d"
    
    response = requests.get(
        f"{jira_url}/rest/api/2/search",
        params={"jql": jql, "maxResults": 1000},
        auth=("user", "api_token")
    )
    
    return response.json()['issues']
```

#### Validaciones en Extracción
- ✅ Verificar conexión a fuentes de datos
- ✅ Validar formato de datos extraídos
- ✅ Registrar timestamp de extracción
- ✅ Manejo de errores y reintentos
- ✅ Log de registros extraídos

---

### 2. Transformación (Transform)

#### Reglas de Transformación

##### A) Limpieza de Datos
```python
def clean_data(raw_data):
    """
    Limpia y normaliza datos extraídos
    """
    cleaned = []
    
    for record in raw_data:
        # Eliminar duplicados
        if is_duplicate(record):
            log_warning(f"Duplicado detectado: {record['id']}")
            continue
        
        # Manejar valores nulos
        record = handle_null_values(record)
        
        # Normalizar fechas
        record['start_date'] = parse_date(record['start_date'])
        
        # Validar rangos
        if record['budget'] < 0:
            log_error(f"Presupuesto inválido: {record['id']}")
            continue
        
        cleaned.append(record)
    
    return cleaned

def handle_null_values(record):
    """
    Estrategias para valores nulos
    """
    # Campos obligatorios
    if not record.get('project_id'):
        raise ValueError("project_id es obligatorio")
    
    # Valores por defecto
    record['complexity'] = record.get('complexity', 'media')
    record['team_size'] = record.get('team_size', 5)
    
    # Imputación
    if not record.get('estimated_hours'):
        record['estimated_hours'] = estimate_hours(record)
    
    return record
```

##### B) Cálculo de KPIs
```python
def calculate_kpis(project_data, defect_data, time_data):
    """
    Calcula KPIs para el dashboard
    """
    kpis = {}
    
    # KPI: Tasa de defectos
    total_loc = sum(p['lines_of_code'] for p in project_data)
    total_defects = len(defect_data)
    kpis['defect_rate'] = (total_defects / total_loc) * 1000  # Por KLOC
    
    # KPI: Velocidad de desarrollo
    total_features = sum(p['features_completed'] for p in project_data)
    total_time = sum(t['hours'] for t in time_data)
    kpis['velocity'] = total_features / (total_time / 40)  # Features por semana
    
    # KPI: Calidad (basado en cobertura de pruebas y defectos)
    avg_coverage = sum(p['test_coverage'] for p in project_data) / len(project_data)
    critical_defects = len([d for d in defect_data if d['severity'] == 'critical'])
    kpis['quality_index'] = (avg_coverage * 0.7) - (critical_defects * 0.3)
    
    # KPI: Rentabilidad
    total_revenue = sum(p['revenue'] for p in project_data)
    total_cost = sum(p['cost'] for p in project_data)
    kpis['profitability'] = ((total_revenue - total_cost) / total_revenue) * 100
    
    # KPI: Satisfacción del cliente (NPS)
    promoters = sum(1 for p in project_data if p['client_rating'] >= 9)
    detractors = sum(1 for p in project_data if p['client_rating'] <= 6)
    kpis['nps'] = ((promoters - detractors) / len(project_data)) * 100
    
    return kpis
```

##### C) Agregaciones OLAP
```python
def build_olap_cube(project_data, client_data, tech_data, quality_data):
    """
    Construye el cubo OLAP multidimensional
    """
    cube = {
        'dimensions': {
            'tiempo': [],
            'tecnologia': [],
            'cliente': [],
            'calidad': []
        },
        'hechos': {
            'ingresos': {},
            'proyectos': {},
            'defectos': {},
            'satisfaccion': {}
        }
    }
    
    # Dimensión Temporal
    for quarter in get_quarters(project_data):
        projects_in_quarter = filter_by_quarter(project_data, quarter)
        
        cube['dimensions']['tiempo'].append({
            'periodo': quarter,
            'proyectos': len(projects_in_quarter),
            'ingresos': sum(p['revenue'] for p in projects_in_quarter),
            'calidad': avg([p['quality_score'] for p in projects_in_quarter])
        })
    
    # Dimensión Tecnológica
    tech_groups = group_by(project_data, 'technology')
    for tech, projects in tech_groups.items():
        cube['dimensions']['tecnologia'].append({
            'tecnologia': tech,
            'proyectos': len(projects),
            'horas': sum(p['hours'] for p in projects),
            'defectos': sum(p['defects'] for p in projects)
        })
    
    # Dimensión Cliente
    client_segments = group_by(client_data, 'segment')
    for segment, clients in client_segments.items():
        client_projects = [p for p in project_data if p['client_id'] in [c['id'] for c in clients]]
        
        cube['dimensions']['cliente'].append({
            'segmento': segment,
            'proyectos': len(client_projects),
            'valor': sum(p['revenue'] for p in client_projects),
            'satisfaccion': avg([c['satisfaction'] for c in clients])
        })
    
    # Dimensión Calidad
    for month in get_months(quality_data):
        quality_in_month = filter_by_month(quality_data, month)
        
        cube['dimensions']['calidad'].append({
            'mes': month,
            'cobertura_pruebas': avg([q['test_coverage'] for q in quality_in_month]),
            'defectos_reportados': sum(q['defects'] for q in quality_in_month),
            'tiempo_resolucion': avg([q['resolution_time'] for q in quality_in_month])
        })
    
    return cube
```

##### D) Balanced Scorecard - OKRs
```python
def calculate_okrs(kpis, targets):
    """
    Calcula el progreso de OKRs para Balanced Scorecard
    """
    okrs = {
        'financiera': [],
        'clientes': [],
        'procesos': [],
        'aprendizaje': []
    }
    
    # Perspectiva Financiera
    okrs['financiera'].append({
        'objetivo': 'Incrementar Rentabilidad',
        'target': targets['profitability'],
        'current': kpis['profitability'],
        'status': 'success' if kpis['profitability'] >= targets['profitability'] else 'warning',
        'key_results': [
            {'kr': 'ROI de proyectos', 'target': 30, 'current': kpis['roi']},
            {'kr': 'Margen de utilidad', 'target': 25, 'current': kpis['margin']},
            {'kr': 'Reducción de costos', 'target': 15, 'current': kpis['cost_reduction']}
        ]
    })
    
    # Perspectiva de Clientes
    okrs['clientes'].append({
        'objetivo': 'Satisfacción del Cliente',
        'target': targets['nps'],
        'current': kpis['nps'],
        'status': 'success' if kpis['nps'] >= targets['nps'] else 'warning',
        'key_results': [
            {'kr': 'NPS Score', 'target': 70, 'current': kpis['nps']},
            {'kr': 'Tasa de retención', 'target': 90, 'current': kpis['retention']},
            {'kr': 'Recomendaciones', 'target': 25, 'current': kpis['referrals']}
        ]
    })
    
    # Perspectiva de Procesos Internos
    okrs['procesos'].append({
        'objetivo': 'Excelencia Operativa',
        'target': targets['quality'],
        'current': kpis['quality_index'],
        'status': 'success' if kpis['quality_index'] >= targets['quality'] else 'warning',
        'key_results': [
            {'kr': 'Entregas a tiempo', 'target': 95, 'current': kpis['on_time_delivery']},
            {'kr': 'Calidad de código', 'target': 85, 'current': kpis['code_quality']},
            {'kr': 'Cobertura de pruebas', 'target': 90, 'current': kpis['test_coverage']}
        ]
    })
    
    # Perspectiva de Aprendizaje
    okrs['aprendizaje'].append({
        'objetivo': 'Desarrollo del Talento',
        'target': targets['training_hours'],
        'current': kpis['training_hours'],
        'status': 'success' if kpis['training_hours'] >= targets['training_hours'] else 'warning',
        'key_results': [
            {'kr': 'Horas de capacitación', 'target': 40, 'current': kpis['training_hours']},
            {'kr': 'Certificaciones', 'target': 15, 'current': kpis['certifications']},
            {'kr': 'Satisfacción laboral', 'target': 85, 'current': kpis['employee_satisfaction']}
        ]
    })
    
    return okrs
```

#### Validaciones en Transformación
- ✅ Verificar integridad referencial
- ✅ Validar rangos de valores
- ✅ Detectar anomalías estadísticas
- ✅ Verificar consistencia temporal
- ✅ Validar cálculos de KPIs

---

### 3. Carga (Load)

#### Destinos de Datos
1. **Base de Datos del Cubo OLAP**
   - Motor: PostgreSQL con extensión cube
   - Tablas: dimensiones (tiempo, tecnologia, cliente, calidad) y hechos
   
2. **Cache Redis**
   - KPIs en tiempo real
   - Datos de dashboard principal
   - TTL: 5 minutos

3. **Base de Datos de Aplicación**
   - Datos operacionales
   - Histórico de predicciones
   - Logs de auditoria

#### Proceso de Carga
```python
def load_to_olap(cube_data):
    """
    Carga datos al cubo OLAP
    """
    conn = psycopg2.connect(olap_connection_string)
    cursor = conn.cursor()
    
    try:
        # Iniciar transacción
        cursor.execute("BEGIN")
        
        # Cargar dimensión temporal
        for record in cube_data['dimensions']['tiempo']:
            cursor.execute("""
                INSERT INTO dim_tiempo (periodo, anio, trimestre, mes)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (periodo) DO UPDATE 
                SET anio = EXCLUDED.anio, trimestre = EXCLUDED.trimestre
            """, (record['periodo'], record['anio'], record['trimestre'], record['mes']))
        
        # Cargar hechos
        for fact in cube_data['hechos']:
            cursor.execute("""
                INSERT INTO fact_proyectos 
                (tiempo_id, tecnologia_id, cliente_id, ingresos, proyectos, defectos)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                fact['tiempo_id'], 
                fact['tecnologia_id'], 
                fact['cliente_id'],
                fact['ingresos'],
                fact['proyectos'],
                fact['defectos']
            ))
        
        # Commit transacción
        cursor.execute("COMMIT")
        log_info(f"Cargados {len(cube_data['hechos'])} registros al cubo OLAP")
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        log_error(f"Error al cargar datos: {str(e)}")
        raise

def load_to_cache(kpis):
    """
    Carga KPIs a Redis para acceso rápido
    """
    redis_client = redis.Redis(host='cache-server', port=6379)
    
    # Cachear KPIs con TTL de 5 minutos
    redis_client.setex(
        'dashboard:kpis',
        300,  # 5 minutos
        json.dumps(kpis)
    )
    
    log_info("KPIs cargados en cache")

def load_okrs(okr_data):
    """
    Carga OKRs calculados
    """
    conn = psycopg2.connect(app_db_connection_string)
    cursor = conn.cursor()
    
    for perspective, objectives in okr_data.items():
        for objective in objectives:
            cursor.execute("""
                INSERT INTO okrs 
                (perspectiva, objetivo, target, current, status, fecha)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                perspective,
                objective['objetivo'],
                objective['target'],
                objective['current'],
                objective['status']
            ))
    
    conn.commit()
```

#### Validaciones en Carga
- ✅ Verificar transacciones exitosas
- ✅ Validar conteo de registros cargados
- ✅ Verificar constraints de base de datos
- ✅ Actualizar timestamps de última carga
- ✅ Generar reporte de carga

---

### 4. Orquestación y Automatización

#### Pipeline ETL con Apache Airflow
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'buap-software',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['etl@buapsoftware.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'dss_etl_pipeline',
    default_args=default_args,
    description='ETL para Sistema de Soporte de Decisión',
    schedule_interval='0 */6 * * *',  # Cada 6 horas
    catchup=False
)

# Tareas de Extracción
extract_projects = PythonOperator(
    task_id='extract_projects',
    python_callable=extract_project_data,
    dag=dag,
)

extract_git = PythonOperator(
    task_id='extract_git_metrics',
    python_callable=extract_git_metrics,
    dag=dag,
)

extract_defects = PythonOperator(
    task_id='extract_defects',
    python_callable=extract_defects,
    dag=dag,
)

# Tarea de Transformación
transform_data = PythonOperator(
    task_id='transform_data',
    python_callable=transform_pipeline,
    dag=dag,
)

# Tareas de Carga
load_olap = PythonOperator(
    task_id='load_olap',
    python_callable=load_to_olap,
    dag=dag,
)

load_cache = PythonOperator(
    task_id='load_cache',
    python_callable=load_to_cache,
    dag=dag,
)

# Tarea de Validación
validate_etl = PythonOperator(
    task_id='validate_etl',
    python_callable=validate_etl_process,
    dag=dag,
)

# Definir dependencias
[extract_projects, extract_git, extract_defects] >> transform_data
transform_data >> [load_olap, load_cache]
[load_olap, load_cache] >> validate_etl
```

#### Monitoreo y Alertas
```python
def validate_etl_process():
    """
    Valida que el proceso ETL se completó correctamente
    """
    validations = {
        'records_extracted': check_extraction_count(),
        'data_quality': check_data_quality(),
        'load_success': check_load_status(),
        'cube_integrity': check_cube_integrity()
    }
    
    if not all(validations.values()):
        send_alert("ETL Pipeline", "Fallo en validación ETL", validations)
        raise Exception("ETL validation failed")
    
    log_info("ETL Pipeline completado exitosamente")
    return True

def send_alert(subject, message, details):
    """
    Envía alertas por email y Slack
    """
    # Email
    send_email(
        to=['team@buapsoftware.com'],
        subject=f"[ALERTA] {subject}",
        body=f"{message}\n\nDetalles: {json.dumps(details, indent=2)}"
    )
    
    # Slack
    slack_webhook = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    requests.post(slack_webhook, json={
        "text": f"🚨 *{subject}*\n{message}",
        "attachments": [{
            "color": "danger",
            "fields": [
                {"title": k, "value": str(v), "short": True}
                for k, v in details.items()
            ]
        }]
    })
```

---

## 📊 Cubo OLAP - Especificaciones Técnicas

### Arquitectura del Cubo

#### Modelo Estrella
```sql
-- Tabla de Hechos
CREATE TABLE fact_proyectos (
    id SERIAL PRIMARY KEY,
    tiempo_id INTEGER REFERENCES dim_tiempo(id),
    tecnologia_id INTEGER REFERENCES dim_tecnologia(id),
    cliente_id INTEGER REFERENCES dim_cliente(id),
    calidad_id INTEGER REFERENCES dim_calidad(id),
    ingresos DECIMAL(12,2),
    costos DECIMAL(12,2),
    proyectos_iniciados INTEGER,
    proyectos_completados INTEGER,
    defectos_criticos INTEGER,
    defectos_totales INTEGER,
    horas_trabajadas INTEGER,
    satisfaccion_cliente DECIMAL(3,2),
    fecha_carga TIMESTAMP DEFAULT NOW()
);

-- Dimensión Temporal
CREATE TABLE dim_tiempo (
    id SERIAL PRIMARY KEY,
    fecha DATE UNIQUE,
    anio INTEGER,
    trimestre INTEGER,
    mes INTEGER,
    semana INTEGER,
    dia_semana VARCHAR(10),
    es_festivo BOOLEAN
);

-- Dimensión Tecnología
CREATE TABLE dim_tecnologia (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50),
    categoria VARCHAR(50),
    version VARCHAR(20),
    popularidad INTEGER
);

-- Dimensión Cliente
CREATE TABLE dim_cliente (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    segmento VARCHAR(50),
    industria VARCHAR(50),
    tamanio VARCHAR(20),
    pais VARCHAR(50)
);

-- Dimensión Calidad
CREATE TABLE dim_calidad (
    id SERIAL PRIMARY KEY,
    nivel_calidad VARCHAR(20),
    cobertura_min DECIMAL(5,2),
    cobertura_max DECIMAL(5,2),
    tasa_defectos_max DECIMAL(5,2)
);
```

#### Operaciones OLAP

##### Drill-Down
```sql
-- De trimestre a mes a día
SELECT 
    t.anio,
    t.trimestre,
    t.mes,
    SUM(f.ingresos) as ingresos_totales,
    SUM(f.proyectos_completados) as proyectos
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
WHERE t.anio = 2024
GROUP BY t.anio, t.trimestre, t.mes
ORDER BY t.trimestre, t.mes;
```

##### Roll-Up
```sql
-- De proyecto individual a segmento de cliente
SELECT 
    c.segmento,
    COUNT(DISTINCT f.id) as total_proyectos,
    SUM(f.ingresos) as ingresos_totales,
    AVG(f.satisfaccion_cliente) as satisfaccion_promedio
FROM fact_proyectos f
JOIN dim_cliente c ON f.cliente_id = c.id
GROUP BY c.segmento;
```

##### Slice
```sql
-- Corte: Solo proyectos de tecnología React
SELECT 
    t.mes,
    t.anio,
    SUM(f.proyectos_completados) as proyectos,
    SUM(f.ingresos) as ingresos
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
JOIN dim_tecnologia tech ON f.tecnologia_id = tech.id
WHERE tech.nombre = 'React'
GROUP BY t.anio, t.mes
ORDER BY t.anio, t.mes;
```

##### Dice
```sql
-- Cubo: React + Gobierno + Q1 2024
SELECT 
    t.mes,
    c.nombre as cliente,
    SUM(f.ingresos) as ingresos,
    SUM(f.proyectos_completados) as proyectos
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
JOIN dim_tecnologia tech ON f.tecnologia_id = tech.id
JOIN dim_cliente c ON f.cliente_id = c.id
WHERE tech.nombre = 'React'
  AND c.segmento = 'Gobierno'
  AND t.anio = 2024
  AND t.trimestre = 1
GROUP BY t.mes, c.nombre;
```

##### Pivot
```sql
-- Pivotear: Tecnologías como columnas, trimestres como filas
SELECT 
    CONCAT('Q', t.trimestre, ' ', t.anio) as periodo,
    SUM(CASE WHEN tech.nombre = 'React' THEN f.proyectos_completados ELSE 0 END) as react,
    SUM(CASE WHEN tech.nombre = 'Angular' THEN f.proyectos_completados ELSE 0 END) as angular,
    SUM(CASE WHEN tech.nombre = 'Vue.js' THEN f.proyectos_completados ELSE 0 END) as vue,
    SUM(CASE WHEN tech.nombre = 'Node.js' THEN f.proyectos_completados ELSE 0 END) as nodejs
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
JOIN dim_tecnologia tech ON f.tecnologia_id = tech.id
GROUP BY t.anio, t.trimestre
ORDER BY t.anio, t.trimestre;
```

---

## 🔮 Modelo Predictivo - Distribución de Rayleigh

### Fundamento Matemático

#### Función de Densidad de Probabilidad
```
f(t; σ) = (t / σ²) × e^(-t² / 2σ²)
```

Donde:
- `t` = tiempo desde el inicio del proyecto
- `σ` = parámetro de escala (relacionado con la dispersión)

#### Función de Distribución Acumulada
```
F(t; σ) = 1 - e^(-t² / 2σ²)
```

#### Momento del Pico
El máximo de la densidad ocurre en:
```
t_peak = σ
```

#### Media y Varianza
```
Media: μ = σ × √(π/2) ≈ 1.253σ
Varianza: σ² × (4 - π) / 2
```

### Implementación del Modelo

#### Algoritmo de Predicción
```python
import numpy as np
from scipy.stats import rayleigh

class RayleighDefectPredictor:
    def __init__(self, project_size, complexity, team_experience, duration):
        self.project_size = project_size  # LOC
        self.complexity = complexity
        self.team_experience = team_experience
        self.duration = duration
        
        # Factores de ajuste
        self.complexity_factors = {
            'baja': 0.8,
            'media': 1.0,
            'alta': 1.3,
            'muy-alta': 1.6
        }
        
        self.experience_factors = {
            'baja': 1.4,
            'media': 1.0,
            'alta': 0.7,
            'experto': 0.5
        }
        
    def estimate_total_defects(self):
        """
        Estima el total de defectos basado en modelo empírico
        """
        # Tasa base: 40 defectos por KLOC (modelo COCOMO)
        base_rate = 40
        
        # Ajustar por complejidad y experiencia
        adjusted_rate = base_rate * \
                       self.complexity_factors[self.complexity] * \
                       self.experience_factors[self.team_experience]
        
        # Calcular total
        kloc = self.project_size / 1000
        total_defects = kloc * adjusted_rate
        
        return int(total_defects)
    
    def calculate_sigma(self):
        """
        Calcula el parámetro sigma de Rayleigh
        El pico típicamente ocurre al 40-60% del proyecto
        """
        # Asumimos pico al 50% del proyecto
        # Como t_peak = σ, entonces σ = 0.5 × duration
        sigma = self.duration * 0.35  # Ajustado empíricamente
        return sigma
    
    def predict_defects_over_time(self, time_points=None):
        """
        Predice defectos a lo largo del tiempo
        """
        if time_points is None:
            time_points = np.linspace(0, self.duration, 100)
        
        sigma = self.calculate_sigma()
        total_defects = self.estimate_total_defects()
        
        # Calcular densidad de probabilidad (defectos nuevos)
        pdf = rayleigh.pdf(time_points, scale=sigma)
        defects_density = pdf * total_defects
        
        # Calcular acumulados
        cdf = rayleigh.cdf(time_points, scale=sigma)
        cumulative_defects = cdf * total_defects
        
        return {
            'time': time_points,
            'density': defects_density,
            'cumulative': cumulative_defects,
            'total': total_defects,
            'sigma': sigma,
            'peak_time': sigma  # El pico está en t = σ
        }
    
    def predict_defects_by_severity(self, total_defects):
        """
        Distribuye defectos por severidad según datos históricos
        """
        # Distribución típica de severidad
        distribution = {
            'criticos': 0.05,   # 5%
            'mayores': 0.15,    # 15%
            'menores': 0.35,    # 35%
            'triviales': 0.45   # 45%
        }
        
        return {
            severity: int(total_defects * percentage)
            for severity, percentage in distribution.items()
        }
    
    def assess_risk(self, total_defects):
        """
        Evalúa el nivel de riesgo del proyecto
        """
        if total_defects > 500:
            return 'alto'
        elif total_defects > 200:
            return 'medio'
        else:
            return 'bajo'
    
    def generate_recommendations(self, prediction):
        """
        Genera recomendaciones basadas en la predicción
        """
        recommendations = []
        
        peak_time = prediction['peak_time']
        total_defects = prediction['total']
        risk = self.assess_risk(total_defects)
        
        # Recomendaciones generales
        recommendations.append({
            'tipo': 'testing',
            'prioridad': 'alta',
            'descripcion': f'Incrementar cobertura de pruebas entre los meses {int(peak_time-2)} y {int(peak_time+2)}'
        })
        
        recommendations.append({
            'tipo': 'code-review',
            'prioridad': 'alta',
            'descripcion': 'Implementar revisiones de código más frecuentes durante la fase crítica'
        })
        
        recommendations.append({
            'tipo': 'recursos',
            'prioridad': 'media',
            'descripcion': f'Planificar recursos adicionales de QA para el mes {int(peak_time)}'
        })
        
        # Recomendaciones específicas por riesgo
        if risk == 'alto':
            recommendations.append({
                'tipo': 'estrategia',
                'prioridad': 'crítica',
                'descripcion': 'Considerar reducir alcance, aumentar experiencia del equipo, o extender timeline'
            })
        
        if self.complexity in ['alta', 'muy-alta']:
            recommendations.append({
                'tipo': 'arquitectura',
                'prioridad': 'alta',
                'descripcion': 'Realizar revisiones de arquitectura para simplificar componentes complejos'
            })
        
        if self.team_experience in ['baja', 'media']:
            recommendations.append({
                'tipo': 'capacitacion',
                'prioridad': 'media',
                'descripcion': 'Programa de capacitación intensivo en tecnologías del proyecto'
            })
        
        return recommendations

# Ejemplo de uso
predictor = RayleighDefectPredictor(
    project_size=10000,      # 10,000 LOC
    complexity='media',
    team_experience='media',
    duration=12              # 12 meses
)

prediction = predictor.predict_defects_over_time()
severity_dist = predictor.predict_defects_by_severity(prediction['total'])
recommendations = predictor.generate_recommendations(prediction)

print(f"Total de defectos estimados: {prediction['total']}")
print(f"Pico de defectos en mes: {prediction['peak_time']:.1f}")
print(f"Distribución por severidad: {severity_dist}")
print(f"Nivel de riesgo: {predictor.assess_risk(prediction['total'])}")
```

### Calibración del Modelo

#### Ajuste con Datos Históricos
```python
def calibrate_model(historical_projects):
    """
    Calibra el modelo con datos históricos de la empresa
    """
    calibration_data = []
    
    for project in historical_projects:
        # Datos reales del proyecto
        actual_defects = project['total_defects']
        actual_peak_time = project['defect_peak_month']
        
        # Predicción con modelo base
        predictor = RayleighDefectPredictor(
            project['size'],
            project['complexity'],
            project['team_experience'],
            project['duration']
        )
        
        predicted = predictor.predict_defects_over_time()
        predicted_defects = predicted['total']
        predicted_peak = predicted['peak_time']
        
        # Calcular error
        error_defects = abs(actual_defects - predicted_defects) / actual_defects
        error_peak = abs(actual_peak_time - predicted_peak) / actual_peak_time
        
        calibration_data.append({
            'project': project['name'],
            'error_defects': error_defects,
            'error_peak': error_peak,
            'adjustment_factor': actual_defects / predicted_defects
        })
    
    # Calcular factor de ajuste promedio
    avg_adjustment = np.mean([d['adjustment_factor'] for d in calibration_data])
    
    return {
        'adjustment_factor': avg_adjustment,
        'mean_error_defects': np.mean([d['error_defects'] for d in calibration_data]),
        'mean_error_peak': np.mean([d['error_peak'] for d in calibration_data]),
        'projects_analyzed': len(calibration_data)
    }
```

#### Actualización Continua
```python
def update_model_with_actuals(project_id, actual_defects_timeline):
    """
    Actualiza el modelo con defectos reales durante el proyecto
    """
    # Obtener predicción original
    original_prediction = get_prediction(project_id)
    
    # Calcular diferencia
    current_month = len(actual_defects_timeline)
    predicted_at_month = original_prediction['cumulative'][current_month]
    actual_at_month = sum(actual_defects_timeline)
    
    # Ajustar predicción restante
    adjustment_factor = actual_at_month / predicted_at_month
    
    # Recalcular sigma basado en datos reales
    if actual_at_month >= original_prediction['total'] * 0.5:
        # Ya pasamos el pico, recalcular sigma
        new_sigma = estimate_sigma_from_data(actual_defects_timeline)
        
        # Actualizar predicción
        update_prediction(project_id, {
            'sigma': new_sigma,
            'adjustment_factor': adjustment_factor,
            'updated_date': datetime.now()
        })
    
    return {
        'adjustment_needed': adjustment_factor,
        'accuracy': 1 - abs(1 - adjustment_factor)
    }
```

---

## 📋 Modelo de Madurez CMMI

### Alineación con CMMI Nivel 4

El Sistema de Soporte de Decisión está diseñado para soportar la certificación CMMI Nivel 4 (Gestionado Cuantitativamente).

#### Áreas de Proceso Cubiertas

##### 1. Gestión Cuantitativa del Proyecto (QPM)
- **Objetivo:** Gestionar cuantitativamente el proyecto según objetivos establecidos

**Implementación en el DSS:**
- Dashboard con KPIs en tiempo real
- Alertas automáticas cuando métricas están fuera de rango
- Comparación continua contra baselines históricas
- Modelo predictivo para anticipar problemas

**Evidencias:**
```python
# Ejemplo: Sistema de alertas basado en umbrales
def monitor_project_metrics(project_id):
    """
    Monitorea métricas del proyecto contra umbrales definidos
    """
    current_metrics = get_current_metrics(project_id)
    thresholds = get_project_thresholds(project_id)
    baseline = get_historical_baseline(project_id)
    
    alerts = []
    
    # Verificar contra umbrales
    if current_metrics['defect_density'] > thresholds['defect_density_max']:
        alerts.append({
            'severity': 'high',
            'metric': 'defect_density',
            'current': current_metrics['defect_density'],
            'threshold': thresholds['defect_density_max'],
            'action': 'Incrementar actividades de QA'
        })
    
    if current_metrics['velocity'] < baseline['velocity'] * 0.8:
        alerts.append({
            'severity': 'medium',
            'metric': 'velocity',
            'current': current_metrics['velocity'],
            'expected': baseline['velocity'],
            'action': 'Revisar impedimentos y capacidad del equipo'
        })
    
    # Generar reporte
    if alerts:
        generate_alert_report(project_id, alerts)
        notify_stakeholders(project_id, alerts)
    
    return alerts
```

##### 2. Rendimiento del Proceso Organizacional (OPP)
- **Objetivo:** Establecer y mantener comprensión cuantitativa del rendimiento de los procesos

**Implementación en el DSS:**
- Cubo OLAP con múltiples dimensiones de análisis
- Baselines de rendimiento por tipo de proyecto
- Análisis de tendencias y patrones
- Capacidad del proceso calculada estadísticamente

**Evidencias:**
```python
# Ejemplo: Cálculo de capacidad del proceso
def calculate_process_capability(process_name, metric_name):
    """
    Calcula la capacidad del proceso usando Control Estadístico de Procesos
    """
    # Obtener datos históricos
    historical_data = get_historical_metrics(process_name, metric_name)
    
    # Calcular estadísticas
    mean = np.mean(historical_data)
    std_dev = np.std(historical_data)
    
    # Especificaciones
    upper_spec_limit = get_specification_limit(process_name, metric_name, 'upper')
    lower_spec_limit = get_specification_limit(process_name, metric_name, 'lower')
    
    # Calcular Cp y Cpk
    cp = (upper_spec_limit - lower_spec_limit) / (6 * std_dev)
    
    cpu = (upper_spec_limit - mean) / (3 * std_dev)
    cpl = (mean - lower_spec_limit) / (3 * std_dev)
    cpk = min(cpu, cpl)
    
    # Interpretar
    capability = {
        'Cp': cp,
        'Cpk': cpk,
        'interpretation': interpret_cpk(cpk),
        'recommendation': recommend_action(cpk)
    }
    
    return capability

def interpret_cpk(cpk):
    """Interpreta el valor de Cpk"""
    if cpk >= 2.0:
        return 'Excelente - Proceso altamente capaz'
    elif cpk >= 1.33:
        return 'Adecuado - Proceso capaz'
    elif cpk >= 1.0:
        return 'Mínimo - Proceso marginalmente capaz'
    else:
        return 'Inadecuado - Proceso no capaz'
```

##### 3. Análisis Causal y Resolución (CAR)
- **Objetivo:** Identificar causas de defectos y otros problemas, y tomar acciones para prevenir recurrencia

**Implementación en el DSS:**
- Análisis de defectos por categoría y causa raíz
- Correlación entre métricas para identificar patrones
- Recomendaciones automáticas basadas en análisis histórico
- Seguimiento de efectividad de acciones correctivas

**Evidencias:**
```python
# Ejemplo: Análisis de causa raíz automatizado
def perform_root_cause_analysis(defect_data):
    """
    Realiza análisis de causa raíz usando datos históricos y ML
    """
    from sklearn.tree import DecisionTreeClassifier
    
    # Preparar datos
    X = prepare_features(defect_data)  # Features: complejidad, tecnología, experiencia, etc.
    y = [d['root_cause'] for d in defect_data]
    
    # Entrenar clasificador
    model = DecisionTreeClassifier(max_depth=5)
    model.fit(X, y)
    
    # Obtener reglas
    rules = extract_rules_from_tree(model)
    
    # Analizar patrones
    patterns = []
    for rule in rules:
        if rule['confidence'] > 0.7:
            patterns.append({
                'pattern': rule['condition'],
                'root_cause': rule['prediction'],
                'frequency': rule['support'],
                'confidence': rule['confidence'],
                'recommended_action': get_preventive_action(rule['prediction'])
            })
    
    return {
        'patterns': patterns,
        'top_causes': get_top_causes(y),
        'recommendations': generate_preventive_recommendations(patterns)
    }

def get_preventive_action(root_cause):
    """Mapea causa raíz a acción preventiva"""
    preventive_actions = {
        'requisitos_incompletos': 'Mejorar proceso de recopilación de requisitos, añadir revisiones adicionales',
        'falta_experiencia': 'Programa de capacitación, pair programming con seniors',
        'complejidad_tecnica': 'Spike técnico previo, revisión de arquitectura',
        'comunicacion_deficiente': 'Daily standups obligatorios, documentación mejorada',
        'presion_tiempo': 'Revisión de estimaciones, negociación de alcance'
    }
    
    return preventive_actions.get(root_cause, 'Realizar análisis detallado')
```

### Métricas CMMI Rastreadas

#### Métricas de Proyecto
```python
PROJECT_METRICS = {
    'schedule_performance': {
        'formula': 'earned_value / planned_value',
        'target': '>= 0.95',
        'source': 'project_management_system'
    },
    'cost_performance': {
        'formula': 'earned_value / actual_cost',
        'target': '>= 0.95',
        'source': 'financial_system'
    },
    'defect_density': {
        'formula': 'total_defects / (size_kloc)',
        'target': '<= 2.0',
        'source': 'defect_tracking_system'
    },
    'requirements_volatility': {
        'formula': 'requirements_changed / total_requirements',
        'target': '<= 0.10',
        'source': 'requirements_management_system'
    }
}
```

#### Métricas de Proceso
```python
PROCESS_METRICS = {
    'peer_review_coverage': {
        'formula': 'artifacts_reviewed / total_artifacts',
        'target': '>= 0.90',
        'source': 'review_system'
    },
    'test_coverage': {
        'formula': 'lines_covered / total_lines',
        'target': '>= 0.85',
        'source': 'ci_cd_system'
    },
    'defect_removal_efficiency': {
        'formula': 'defects_found_pre_release / total_defects',
        'target': '>= 0.90',
        'source': 'quality_management_system'
    },
    'process_compliance': {
        'formula': 'compliant_activities / total_activities',
        'target': '>= 0.95',
        'source': 'process_management_system'
    }
}
```

### Auditoría y Trazabilidad

```python
def generate_cmmi_audit_report(start_date, end_date):
    """
    Genera reporte de auditoría para CMMI
    """
    report = {
        'period': {'start': start_date, 'end': end_date},
        'metrics_summary': {},
        'process_compliance': {},
        'deficiencies': [],
        'improvements': []
    }
    
    # Resumir métricas
    for metric_name, metric_def in PROJECT_METRICS.items():
        data = get_metric_data(metric_name, start_date, end_date)
        
        report['metrics_summary'][metric_name] = {
            'mean': np.mean(data),
            'std_dev': np.std(data),
            'target': metric_def['target'],
            'in_compliance': check_compliance(data, metric_def['target']),
            'trend': calculate_trend(data)
        }
    
    # Verificar cumplimiento de procesos
    for process in DEFINED_PROCESSES:
        compliance = audit_process_compliance(process, start_date, end_date)
        report['process_compliance'][process['name']] = compliance
        
        if compliance['percentage'] < 0.95:
            report['deficiencies'].append({
                'process': process['name'],
                'compliance': compliance['percentage'],
                'issues': compliance['issues']
            })
    
    # Identificar mejoras
    improvements = identify_improvement_opportunities(report['metrics_summary'])
    report['improvements'] = improvements
    
    # Generar documentación
    save_audit_report(report)
    
    return report
```

---

## 🔧 Procedimientos de Operación Estándar

### Procedimiento: Ejecución del Pipeline ETL

#### 1. Preparación
- [ ] Verificar disponibilidad de fuentes de datos
- [ ] Validar credenciales de conexión
- [ ] Revisar espacio en disco
- [ ] Verificar que no haya ejecución en progreso

#### 2. Ejecución
```bash
# Iniciar pipeline ETL
airflow trigger_dag dss_etl_pipeline

# Monitorear progreso
airflow dag state dss_etl_pipeline

# Ver logs en tiempo real
airflow logs dss_etl_pipeline extract_projects
```

#### 3. Validación
- [ ] Verificar conteo de registros extraídos
- [ ] Revisar calidad de datos transformados
- [ ] Confirmar carga exitosa al cubo OLAP
- [ ] Validar actualización de cache Redis
- [ ] Ejecutar queries de validación

#### 4. Resolución de Problemas
| Problema | Causa Posible | Solución |
|----------|---------------|----------|
| Fallo en extracción | Timeout de base de datos | Aumentar timeout, verificar carga del servidor |
| Datos duplicados | Re-ejecución sin limpiar staging | Limpiar tablas staging antes de reintentar |
| Error de transformación | Datos inesperados | Revisar logs, añadir validación adicional |
| Fallo en carga | Constraint violation | Revisar integridad referencial, corregir datos |

### Procedimiento: Actualización del Modelo Predictivo

#### 1. Recopilación de Datos Reales
```python
# Registrar defectos reales del proyecto
def register_actual_defects(project_id, month, defects_count, severity_dist):
    """
    Registra defectos reales para calibración del modelo
    """
    insert_actual_defects(project_id, {
        'month': month,
        'defects_count': defects_count,
        'critical': severity_dist['critical'],
        'major': severity_dist['major'],
        'minor': severity_dist['minor'],
        'trivial': severity_dist['trivial'],
        'timestamp': datetime.now()
    })
    
    # Trigger recalibración si es necesario
    if month >= get_project_duration(project_id) * 0.5:
        recalibrate_model(project_id)
```

#### 2. Calibración
- [ ] Comparar predicciones vs. realidad
- [ ] Calcular error medio
- [ ] Ajustar factores de complejidad/experiencia
- [ ] Re-entrenar si error > 20%
- [ ] Documentar ajustes realizados

#### 3. Validación
- [ ] Ejecutar predicciones de prueba
- [ ] Validar con equipo de QA
- [ ] Revisar recomendaciones generadas
- [ ] Aprobar para producción

### Procedimiento: Generación de Reportes Ejecutivos

#### 1. Dashboard Ejecutivo Semanal
```python
def generate_executive_report(week_number):
    """
    Genera reporte ejecutivo semanal
    """
    report = {
        'period': f'Semana {week_number}',
        'kpis': get_weekly_kpis(week_number),
        'okrs': get_okr_progress(),
        'projects': get_project_summary(week_number),
        'risks': identify_risks(),
        'achievements': get_achievements(week_number)
    }
    
    # Generar PDF
    pdf = generate_pdf_report(report, template='executive_weekly')
    
    # Enviar a stakeholders
    send_email(
        to=get_executive_distribution_list(),
        subject=f'Reporte Ejecutivo - Semana {week_number}',
        body='Adjunto reporte ejecutivo semanal',
        attachments=[pdf]
    )
    
    return report
```

#### 2. Balanced Scorecard Mensual
- [ ] Recopilar datos de OKRs
- [ ] Calcular progreso por perspectiva
- [ ] Identificar objetivos en riesgo
- [ ] Generar gráfico radar
- [ ] Preparar presentación
- [ ] Revisar con liderazgo
- [ ] Publicar en portal interno

#### 3. Análisis OLAP Trimestral
- [ ] Ejecutar análisis multidimensional
- [ ] Identificar tendencias
- [ ] Comparar contra baselines
- [ ] Drill-down en áreas problemáticas
- [ ] Generar insights accionables
- [ ] Presentar a junta directiva

---

## 📊 Métricas de Éxito del DSS

### KPIs del Sistema

1. **Disponibilidad del Sistema**
   - Target: 99.5% uptime
   - Medición: Monitoreo continuo con Pingdom

2. **Latencia de Dashboards**
   - Target: < 2 segundos para carga inicial
   - Target: < 500ms para interacciones
   - Medición: Real User Monitoring (RUM)

3. **Precisión de Predicciones**
   - Target: Error < 15% en predicción de defectos
   - Medición: Comparación mensual con datos reales

4. **Adopción por Usuarios**
   - Target: 90% de gerentes de proyecto usan el sistema semanalmente
   - Medición: Analytics de uso

5. **Impacto en Toma de Decisiones**
   - Target: 80% de decisiones estratégicas basadas en datos del DSS
   - Medición: Encuestas trimestrales

---

## 🔒 Seguridad y Cumplimiento

### Control de Acceso

```python
ROLES = {
    'admin': {
        'permissions': ['read', 'write', 'delete', 'admin'],
        'access': ['all']
    },
    'project_manager': {
        'permissions': ['read', 'write'],
        'access': ['dashboard', 'olap', 'balanced_scorecard', 'predictive_model']
    },
    'developer': {
        'permissions': ['read'],
        'access': ['dashboard', 'olap']
    },
    'executive': {
        'permissions': ['read'],
        'access': ['dashboard', 'balanced_scorecard']
    }
}
```

### Auditoría
- Todos los accesos son registrados
- Cambios en datos son auditados
- Logs de errores son preservados por 1 año
- Backups diarios con retención de 30 días

---

**Documento vivo - Última actualización: Noviembre 2024**

*Este documento debe ser revisado trimestralmente y actualizado con mejoras al proceso.*
