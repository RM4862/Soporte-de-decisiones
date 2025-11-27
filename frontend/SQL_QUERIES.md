# Ejemplos de Consultas SQL para Cubo OLAP

Este archivo contiene ejemplos de consultas SQL para implementar el cubo OLAP del Sistema de Soporte de Decisión.

## 📊 Estructura de Tablas

### Tabla de Hechos
```sql
CREATE TABLE fact_proyectos (
    id SERIAL PRIMARY KEY,
    tiempo_id INTEGER REFERENCES dim_tiempo(id),
    tecnologia_id INTEGER REFERENCES dim_tecnologia(id),
    cliente_id INTEGER REFERENCES dim_cliente(id),
    calidad_id INTEGER REFERENCES dim_calidad(id),
    
    -- Métricas
    ingresos DECIMAL(12,2),
    costos DECIMAL(12,2),
    utilidad DECIMAL(12,2),
    proyectos_iniciados INTEGER,
    proyectos_completados INTEGER,
    defectos_criticos INTEGER,
    defectos_mayores INTEGER,
    defectos_menores INTEGER,
    defectos_triviales INTEGER,
    defectos_totales INTEGER,
    horas_trabajadas INTEGER,
    horas_estimadas INTEGER,
    satisfaccion_cliente DECIMAL(3,2),
    nps_score INTEGER,
    
    -- Metadata
    fecha_carga TIMESTAMP DEFAULT NOW(),
    usuario_carga VARCHAR(50)
);

-- Índices para optimizar consultas OLAP
CREATE INDEX idx_fact_tiempo ON fact_proyectos(tiempo_id);
CREATE INDEX idx_fact_tecnologia ON fact_proyectos(tecnologia_id);
CREATE INDEX idx_fact_cliente ON fact_proyectos(cliente_id);
CREATE INDEX idx_fact_calidad ON fact_proyectos(calidad_id);
```

### Dimensiones

```sql
-- Dimensión Temporal
CREATE TABLE dim_tiempo (
    id SERIAL PRIMARY KEY,
    fecha DATE UNIQUE NOT NULL,
    anio INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    mes_nombre VARCHAR(20),
    semana INTEGER,
    dia_mes INTEGER,
    dia_semana INTEGER,
    dia_semana_nombre VARCHAR(20),
    es_festivo BOOLEAN DEFAULT FALSE,
    es_fin_semana BOOLEAN DEFAULT FALSE
);

-- Índices
CREATE INDEX idx_tiempo_fecha ON dim_tiempo(fecha);
CREATE INDEX idx_tiempo_anio_trimestre ON dim_tiempo(anio, trimestre);
CREATE INDEX idx_tiempo_anio_mes ON dim_tiempo(anio, mes);

-- Dimensión Tecnología
CREATE TABLE dim_tecnologia (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    categoria VARCHAR(50),
    tipo VARCHAR(30),
    version VARCHAR(20),
    popularidad INTEGER,
    curva_aprendizaje VARCHAR(20),
    madurez VARCHAR(20)
);

-- Dimensión Cliente
CREATE TABLE dim_cliente (
    id SERIAL PRIMARY KEY,
    codigo_cliente VARCHAR(20) UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    segmento VARCHAR(50),
    industria VARCHAR(50),
    tamanio VARCHAR(20),
    pais VARCHAR(50),
    region VARCHAR(50),
    antiguedad_meses INTEGER,
    nivel_estrategico VARCHAR(20)
);

-- Dimensión Calidad
CREATE TABLE dim_calidad (
    id SERIAL PRIMARY KEY,
    nivel_calidad VARCHAR(20) UNIQUE,
    cobertura_pruebas_min DECIMAL(5,2),
    cobertura_pruebas_max DECIMAL(5,2),
    tasa_defectos_min DECIMAL(5,2),
    tasa_defectos_max DECIMAL(5,2),
    clasificacion VARCHAR(20)
);
```

## 📈 Consultas de Análisis OLAP

### 1. Análisis Temporal

#### Evolución de Ingresos por Trimestre
```sql
SELECT 
    t.anio,
    t.trimestre,
    CONCAT('Q', t.trimestre, ' ', t.anio) as periodo,
    SUM(f.ingresos) as ingresos_totales,
    SUM(f.costos) as costos_totales,
    SUM(f.utilidad) as utilidad_total,
    SUM(f.proyectos_completados) as proyectos_completados,
    AVG(f.satisfaccion_cliente) as satisfaccion_promedio,
    SUM(f.defectos_totales) as defectos_totales
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
WHERE t.anio >= 2024
GROUP BY t.anio, t.trimestre
ORDER BY t.anio, t.trimestre;
```

#### Tendencia Mensual con Comparación YoY
```sql
WITH datos_mensuales AS (
    SELECT 
        t.anio,
        t.mes,
        t.mes_nombre,
        SUM(f.ingresos) as ingresos,
        SUM(f.proyectos_completados) as proyectos,
        AVG(f.satisfaccion_cliente) as satisfaccion
    FROM fact_proyectos f
    JOIN dim_tiempo t ON f.tiempo_id = t.id
    GROUP BY t.anio, t.mes, t.mes_nombre
)
SELECT 
    dm1.anio,
    dm1.mes,
    dm1.mes_nombre,
    dm1.ingresos as ingresos_actual,
    dm2.ingresos as ingresos_anio_anterior,
    ROUND(((dm1.ingresos - dm2.ingresos) / dm2.ingresos * 100), 2) as variacion_porcentual,
    dm1.proyectos as proyectos_actual,
    dm2.proyectos as proyectos_anio_anterior,
    dm1.satisfaccion as satisfaccion_actual,
    dm2.satisfaccion as satisfaccion_anio_anterior
FROM datos_mensuales dm1
LEFT JOIN datos_mensuales dm2 
    ON dm1.mes = dm2.mes 
    AND dm1.anio = dm2.anio + 1
ORDER BY dm1.anio DESC, dm1.mes;
```

### 2. Análisis por Tecnología

#### Ranking de Tecnologías por Rentabilidad
```sql
SELECT 
    tech.nombre as tecnologia,
    tech.categoria,
    COUNT(DISTINCT f.id) as total_proyectos,
    SUM(f.ingresos) as ingresos_totales,
    SUM(f.costos) as costos_totales,
    SUM(f.utilidad) as utilidad_total,
    ROUND(SUM(f.utilidad) / SUM(f.ingresos) * 100, 2) as margen_porcentaje,
    SUM(f.horas_trabajadas) as horas_totales,
    SUM(f.defectos_totales) as defectos_totales,
    ROUND(SUM(f.defectos_totales)::NUMERIC / SUM(f.horas_trabajadas) * 1000, 2) as defectos_por_1000h
FROM fact_proyectos f
JOIN dim_tecnologia tech ON f.tecnologia_id = tech.id
GROUP BY tech.id, tech.nombre, tech.categoria
HAVING COUNT(DISTINCT f.id) >= 3
ORDER BY utilidad_total DESC;
```

#### Matriz de Tecnología vs Complejidad
```sql
SELECT 
    tech.nombre as tecnologia,
    cal.nivel_calidad as nivel_complejidad,
    COUNT(*) as cantidad_proyectos,
    AVG(f.horas_trabajadas) as promedio_horas,
    AVG(f.defectos_totales) as promedio_defectos,
    AVG(f.satisfaccion_cliente) as promedio_satisfaccion
FROM fact_proyectos f
JOIN dim_tecnologia tech ON f.tecnologia_id = tech.id
JOIN dim_calidad cal ON f.calidad_id = cal.id
GROUP BY tech.nombre, cal.nivel_calidad
ORDER BY tech.nombre, cal.nivel_calidad;
```

### 3. Análisis por Cliente

#### Segmentación de Clientes (RFM adaptado)
```sql
WITH metricas_cliente AS (
    SELECT 
        c.id,
        c.nombre,
        c.segmento,
        c.industria,
        COUNT(DISTINCT f.id) as total_proyectos,
        SUM(f.ingresos) as ingresos_totales,
        AVG(f.satisfaccion_cliente) as satisfaccion_promedio,
        MAX(t.fecha) as ultima_interaccion,
        EXTRACT(DAYS FROM NOW() - MAX(t.fecha)) as dias_desde_ultima_interaccion
    FROM dim_cliente c
    JOIN fact_proyectos f ON c.id = f.cliente_id
    JOIN dim_tiempo t ON f.tiempo_id = t.id
    GROUP BY c.id, c.nombre, c.segmento, c.industria
),
percentiles AS (
    SELECT 
        PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY dias_desde_ultima_interaccion) as p33_recencia,
        PERCENTILE_CONT(0.67) WITHIN GROUP (ORDER BY dias_desde_ultima_interaccion) as p67_recencia,
        PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY total_proyectos) as p33_frecuencia,
        PERCENTILE_CONT(0.67) WITHIN GROUP (ORDER BY total_proyectos) as p67_frecuencia,
        PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY ingresos_totales) as p33_valor,
        PERCENTILE_CONT(0.67) WITHIN GROUP (ORDER BY ingresos_totales) as p67_valor
    FROM metricas_cliente
)
SELECT 
    mc.*,
    CASE 
        WHEN mc.dias_desde_ultima_interaccion <= p.p33_recencia THEN 'Alta'
        WHEN mc.dias_desde_ultima_interaccion <= p.p67_recencia THEN 'Media'
        ELSE 'Baja'
    END as recencia,
    CASE 
        WHEN mc.total_proyectos >= p.p67_frecuencia THEN 'Alta'
        WHEN mc.total_proyectos >= p.p33_frecuencia THEN 'Media'
        ELSE 'Baja'
    END as frecuencia,
    CASE 
        WHEN mc.ingresos_totales >= p.p67_valor THEN 'Alto'
        WHEN mc.ingresos_totales >= p.p33_valor THEN 'Medio'
        ELSE 'Bajo'
    END as valor,
    CASE 
        WHEN mc.satisfaccion_promedio >= 0.9 THEN 'Promotor'
        WHEN mc.satisfaccion_promedio >= 0.7 THEN 'Pasivo'
        ELSE 'Detractor'
    END as tipo_nps
FROM metricas_cliente mc
CROSS JOIN percentiles p
ORDER BY mc.ingresos_totales DESC;
```

#### Top Clientes por Segmento
```sql
WITH ranking_clientes AS (
    SELECT 
        c.segmento,
        c.nombre as cliente,
        SUM(f.ingresos) as ingresos_totales,
        COUNT(DISTINCT f.id) as total_proyectos,
        AVG(f.satisfaccion_cliente) as satisfaccion_promedio,
        ROW_NUMBER() OVER (PARTITION BY c.segmento ORDER BY SUM(f.ingresos) DESC) as ranking
    FROM fact_proyectos f
    JOIN dim_cliente c ON f.cliente_id = c.id
    GROUP BY c.segmento, c.nombre
)
SELECT 
    segmento,
    cliente,
    ingresos_totales,
    total_proyectos,
    ROUND(satisfaccion_promedio::NUMERIC, 2) as satisfaccion,
    ranking
FROM ranking_clientes
WHERE ranking <= 5
ORDER BY segmento, ranking;
```

### 4. Análisis de Calidad

#### Evolución de Métricas de Calidad
```sql
SELECT 
    t.anio,
    t.trimestre,
    AVG(cal.cobertura_pruebas_min) as cobertura_promedio,
    SUM(f.defectos_criticos) as defectos_criticos,
    SUM(f.defectos_mayores) as defectos_mayores,
    SUM(f.defectos_menores) as defectos_menores,
    SUM(f.defectos_triviales) as defectos_triviales,
    SUM(f.defectos_totales) as defectos_totales,
    ROUND(
        SUM(f.defectos_totales)::NUMERIC / 
        NULLIF(SUM(f.horas_trabajadas), 0) * 1000, 
        2
    ) as defectos_por_1000h,
    AVG(f.satisfaccion_cliente) as satisfaccion_promedio
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
JOIN dim_calidad cal ON f.calidad_id = cal.id
GROUP BY t.anio, t.trimestre
ORDER BY t.anio, t.trimestre;
```

#### Correlación Calidad vs Satisfacción del Cliente
```sql
SELECT 
    cal.nivel_calidad,
    cal.cobertura_pruebas_min,
    cal.cobertura_pruebas_max,
    COUNT(*) as cantidad_proyectos,
    AVG(f.satisfaccion_cliente) as satisfaccion_promedio,
    STDDEV(f.satisfaccion_cliente) as desviacion_satisfaccion,
    SUM(f.defectos_totales) as defectos_totales,
    AVG(f.defectos_totales) as promedio_defectos,
    SUM(f.ingresos) as ingresos_totales,
    SUM(f.utilidad) as utilidad_total
FROM fact_proyectos f
JOIN dim_calidad cal ON f.calidad_id = cal.id
GROUP BY cal.nivel_calidad, cal.cobertura_pruebas_min, cal.cobertura_pruebas_max
ORDER BY cal.cobertura_pruebas_min DESC;
```

### 5. Operaciones OLAP Avanzadas

#### Drill-Down: De Año → Trimestre → Mes → Día
```sql
-- Nivel 1: Año
SELECT 
    t.anio,
    SUM(f.ingresos) as ingresos,
    SUM(f.proyectos_completados) as proyectos
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
GROUP BY t.anio
ORDER BY t.anio DESC;

-- Nivel 2: Trimestre dentro de año específico
SELECT 
    t.anio,
    t.trimestre,
    SUM(f.ingresos) as ingresos,
    SUM(f.proyectos_completados) as proyectos
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
WHERE t.anio = 2024
GROUP BY t.anio, t.trimestre
ORDER BY t.trimestre;

-- Nivel 3: Mes dentro de trimestre específico
SELECT 
    t.anio,
    t.trimestre,
    t.mes,
    t.mes_nombre,
    SUM(f.ingresos) as ingresos,
    SUM(f.proyectos_completados) as proyectos
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
WHERE t.anio = 2024 AND t.trimestre = 1
GROUP BY t.anio, t.trimestre, t.mes, t.mes_nombre
ORDER BY t.mes;

-- Nivel 4: Día dentro de mes específico
SELECT 
    t.fecha,
    t.dia_semana_nombre,
    SUM(f.ingresos) as ingresos,
    SUM(f.proyectos_completados) as proyectos
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
WHERE t.anio = 2024 AND t.mes = 1
GROUP BY t.fecha, t.dia_semana_nombre
ORDER BY t.fecha;
```

#### Roll-Up: De Cliente Individual → Segmento → Región
```sql
-- Nivel detallado: Cliente individual
SELECT 
    c.nombre as cliente,
    c.segmento,
    c.region,
    SUM(f.ingresos) as ingresos,
    COUNT(*) as proyectos
FROM fact_proyectos f
JOIN dim_cliente c ON f.cliente_id = c.id
GROUP BY c.nombre, c.segmento, c.region
ORDER BY ingresos DESC;

-- Roll-up a Segmento
SELECT 
    c.segmento,
    c.region,
    COUNT(DISTINCT c.id) as clientes,
    SUM(f.ingresos) as ingresos,
    COUNT(*) as proyectos
FROM fact_proyectos f
JOIN dim_cliente c ON f.cliente_id = c.id
GROUP BY c.segmento, c.region
ORDER BY ingresos DESC;

-- Roll-up a Región
SELECT 
    c.region,
    COUNT(DISTINCT c.id) as clientes,
    COUNT(DISTINCT c.segmento) as segmentos,
    SUM(f.ingresos) as ingresos,
    COUNT(*) as proyectos
FROM fact_proyectos f
JOIN dim_cliente c ON f.cliente_id = c.id
GROUP BY c.region
ORDER BY ingresos DESC;
```

#### Slice: Vista de una dimensión específica
```sql
-- Slice: Solo proyectos con tecnología React
SELECT 
    t.anio,
    t.trimestre,
    c.segmento,
    SUM(f.ingresos) as ingresos,
    COUNT(*) as proyectos,
    AVG(f.satisfaccion_cliente) as satisfaccion
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
JOIN dim_cliente c ON f.cliente_id = c.id
JOIN dim_tecnologia tech ON f.tecnologia_id = tech.id
WHERE tech.nombre = 'React'
GROUP BY t.anio, t.trimestre, c.segmento
ORDER BY t.anio DESC, t.trimestre, ingresos DESC;
```

#### Dice: Subcubo con múltiples filtros
```sql
-- Dice: React + Gobierno + Q1 2024 + Alta Calidad
SELECT 
    t.mes_nombre,
    c.nombre as cliente,
    SUM(f.ingresos) as ingresos,
    SUM(f.proyectos_completados) as proyectos,
    AVG(f.satisfaccion_cliente) as satisfaccion,
    SUM(f.defectos_totales) as defectos
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
JOIN dim_cliente c ON f.cliente_id = c.id
JOIN dim_tecnologia tech ON f.tecnologia_id = tech.id
JOIN dim_calidad cal ON f.calidad_id = cal.id
WHERE 
    tech.nombre = 'React'
    AND c.segmento = 'Gobierno'
    AND t.anio = 2024
    AND t.trimestre = 1
    AND cal.nivel_calidad = 'Alta'
GROUP BY t.mes, t.mes_nombre, c.nombre
ORDER BY t.mes;
```

#### Pivot: Tecnologías como columnas
```sql
SELECT 
    CONCAT('Q', t.trimestre, ' ', t.anio) as periodo,
    SUM(CASE WHEN tech.nombre = 'React' THEN f.proyectos_completados ELSE 0 END) as react,
    SUM(CASE WHEN tech.nombre = 'Angular' THEN f.proyectos_completados ELSE 0 END) as angular,
    SUM(CASE WHEN tech.nombre = 'Vue.js' THEN f.proyectos_completados ELSE 0 END) as vue,
    SUM(CASE WHEN tech.nombre = 'Node.js' THEN f.proyectos_completados ELSE 0 END) as nodejs,
    SUM(CASE WHEN tech.nombre = 'Python' THEN f.proyectos_completados ELSE 0 END) as python,
    SUM(CASE WHEN tech.nombre = 'Java' THEN f.proyectos_completados ELSE 0 END) as java,
    SUM(f.proyectos_completados) as total
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
JOIN dim_tecnologia tech ON f.tecnologia_id = tech.id
WHERE t.anio >= 2024
GROUP BY t.anio, t.trimestre
ORDER BY t.anio, t.trimestre;
```

### 6. Análisis Predictivo con SQL

#### Tendencia de Crecimiento
```sql
WITH serie_temporal AS (
    SELECT 
        t.anio,
        t.mes,
        SUM(f.ingresos) as ingresos,
        ROW_NUMBER() OVER (ORDER BY t.anio, t.mes) as periodo
    FROM fact_proyectos f
    JOIN dim_tiempo t ON f.tiempo_id = t.id
    GROUP BY t.anio, t.mes
),
regresion AS (
    SELECT 
        AVG(periodo) as x_medio,
        AVG(ingresos) as y_medio,
        COUNT(*) as n
    FROM serie_temporal
)
SELECT 
    st.anio,
    st.mes,
    st.ingresos as ingresos_reales,
    ROUND(
        r.y_medio + 
        (SUM((st.periodo - r.x_medio) * (st.ingresos - r.y_medio)) OVER (ORDER BY st.periodo) / 
         NULLIF(SUM(POWER(st.periodo - r.x_medio, 2)) OVER (ORDER BY st.periodo), 0)) *
        (st.periodo - r.x_medio),
        2
    ) as tendencia,
    ROUND(st.ingresos - r.y_medio, 2) as desviacion
FROM serie_temporal st
CROSS JOIN regresion r
ORDER BY st.periodo;
```

#### Detección de Anomalías
```sql
WITH estadisticas AS (
    SELECT 
        AVG(ingresos) as media,
        STDDEV(ingresos) as desviacion
    FROM fact_proyectos
)
SELECT 
    t.anio,
    t.mes,
    c.nombre as cliente,
    f.ingresos,
    e.media,
    e.desviacion,
    ROUND((f.ingresos - e.media) / NULLIF(e.desviacion, 0), 2) as z_score,
    CASE 
        WHEN ABS((f.ingresos - e.media) / NULLIF(e.desviacion, 0)) > 3 THEN 'Anomalía Extrema'
        WHEN ABS((f.ingresos - e.media) / NULLIF(e.desviacion, 0)) > 2 THEN 'Anomalía Moderada'
        ELSE 'Normal'
    END as clasificacion
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
JOIN dim_cliente c ON f.cliente_id = c.id
CROSS JOIN estadisticas e
WHERE ABS((f.ingresos - e.media) / NULLIF(e.desviacion, 0)) > 2
ORDER BY ABS((f.ingresos - e.media) / NULLIF(e.desviacion, 0)) DESC;
```

## 🔍 Views Materializadas para Performance

```sql
-- Vista materializada para dashboard principal
CREATE MATERIALIZED VIEW mv_dashboard_kpis AS
SELECT 
    DATE_TRUNC('day', NOW()) as fecha_snapshot,
    COUNT(DISTINCT CASE WHEN t.fecha >= DATE_TRUNC('month', NOW()) THEN f.id END) as proyectos_activos,
    SUM(CASE WHEN t.fecha >= DATE_TRUNC('month', NOW()) THEN f.ingresos ELSE 0 END) as ingresos_mensuales,
    AVG(CASE WHEN t.fecha >= DATE_TRUNC('month', NOW()) THEN f.satisfaccion_cliente END) as satisfaccion_promedio,
    SUM(CASE WHEN t.fecha >= DATE_TRUNC('month', NOW()) THEN f.defectos_criticos ELSE 0 END) as defectos_criticos
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id;

CREATE UNIQUE INDEX ON mv_dashboard_kpis (fecha_snapshot);

-- Refrescar cada hora
CREATE OR REPLACE FUNCTION refresh_dashboard_kpis()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_kpis;
END;
$$ LANGUAGE plpgsql;

-- Vista para análisis OLAP temporal
CREATE MATERIALIZED VIEW mv_olap_temporal AS
SELECT 
    t.anio,
    t.trimestre,
    t.mes,
    SUM(f.ingresos) as ingresos,
    SUM(f.proyectos_completados) as proyectos,
    AVG(f.satisfaccion_cliente) as calidad,
    COUNT(DISTINCT f.cliente_id) as clientes
FROM fact_proyectos f
JOIN dim_tiempo t ON f.tiempo_id = t.id
GROUP BY t.anio, t.trimestre, t.mes;

CREATE INDEX ON mv_olap_temporal (anio, trimestre, mes);
```

## 📊 Procedimientos Almacenados Útiles

```sql
-- Procedimiento para insertar hechos con validación
CREATE OR REPLACE FUNCTION insert_fact_proyecto(
    p_tiempo_id INTEGER,
    p_tecnologia_id INTEGER,
    p_cliente_id INTEGER,
    p_calidad_id INTEGER,
    p_ingresos DECIMAL,
    p_costos DECIMAL,
    p_proyectos_completados INTEGER,
    p_defectos_totales INTEGER,
    p_horas_trabajadas INTEGER,
    p_satisfaccion_cliente DECIMAL
) RETURNS INTEGER AS $$
DECLARE
    v_fact_id INTEGER;
    v_utilidad DECIMAL;
BEGIN
    -- Calcular utilidad
    v_utilidad := p_ingresos - p_costos;
    
    -- Validaciones
    IF p_ingresos < 0 OR p_costos < 0 THEN
        RAISE EXCEPTION 'Ingresos y costos deben ser positivos';
    END IF;
    
    IF p_satisfaccion_cliente < 0 OR p_satisfaccion_cliente > 1 THEN
        RAISE EXCEPTION 'Satisfacción debe estar entre 0 y 1';
    END IF;
    
    -- Insertar
    INSERT INTO fact_proyectos (
        tiempo_id, tecnologia_id, cliente_id, calidad_id,
        ingresos, costos, utilidad, proyectos_completados,
        defectos_totales, horas_trabajadas, satisfaccion_cliente
    ) VALUES (
        p_tiempo_id, p_tecnologia_id, p_cliente_id, p_calidad_id,
        p_ingresos, p_costos, v_utilidad, p_proyectos_completados,
        p_defectos_totales, p_horas_trabajadas, p_satisfaccion_cliente
    )
    RETURNING id INTO v_fact_id;
    
    RETURN v_fact_id;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener KPIs del periodo
CREATE OR REPLACE FUNCTION get_kpis_periodo(
    p_fecha_inicio DATE,
    p_fecha_fin DATE
) RETURNS TABLE (
    total_ingresos DECIMAL,
    total_proyectos INTEGER,
    satisfaccion_promedio DECIMAL,
    defectos_totales INTEGER,
    margen_utilidad DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        SUM(f.ingresos)::DECIMAL,
        SUM(f.proyectos_completados)::INTEGER,
        AVG(f.satisfaccion_cliente)::DECIMAL,
        SUM(f.defectos_totales)::INTEGER,
        (SUM(f.utilidad) / NULLIF(SUM(f.ingresos), 0) * 100)::DECIMAL
    FROM fact_proyectos f
    JOIN dim_tiempo t ON f.tiempo_id = t.id
    WHERE t.fecha BETWEEN p_fecha_inicio AND p_fecha_fin;
END;
$$ LANGUAGE plpgsql;
```

---

**Nota:** Estas consultas son ejemplos para implementar un cubo OLAP robusto. Ajusta según tus necesidades específicas.
