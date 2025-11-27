DROP SCHEMA IF EXISTS `DSS_Proyectos`;
CREATE SCHEMA `DSS_Proyectos`;
USE `DSS_Proyectos`;

-- ==============================
-- DIMENSIONES
-- ==============================

CREATE TABLE IF NOT EXISTS Dim_Proyecto (
    id_proyecto INT PRIMARY KEY,
    nombre VARCHAR(100),
    metodologia VARCHAR(100),
    etapas VARCHAR(100),
    fecha_inicio DATE,
    fecha_fin DATE,
    horas_invertidas INT,
    estado VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Dim_Cliente (
    id_cliente INT PRIMARY KEY,
    nombre VARCHAR(100),
    sector VARCHAR(50),
    pais VARCHAR(50),
    contacto_nombre VARCHAR(100),
    contacto_email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Dim_Responsable (
    id_responsable INT PRIMARY KEY,
    nombre VARCHAR(100),
    rol VARCHAR(50),
    equipo_asignado VARCHAR(100),
    correo VARCHAR(100),
    telefono VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Dim_Tiempo (
    id_tiempo INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE,
    dia INT,
    mes INT,
    trimestre INT,
    anio INT
);

CREATE TABLE IF NOT EXISTS Dim_Tarea (
    id_tarea INT PRIMARY KEY,
    titulo VARCHAR(100),
    prioridad VARCHAR(20),
    descripcion TEXT,
    estado VARCHAR(20),
    fecha_inicio DATE,
    fecha_fin DATE
);

-- ==============================
-- TABLAS DE HECHOS
-- ==============================

-- Fact de Proyectos
CREATE TABLE IF NOT EXISTS Fact_Proyectos (
    id_fact_proyecto INT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT,
    id_cliente INT,
    id_responsable INT,
    id_tiempo INT,
    presupuesto DECIMAL(12,2),
    costo_total DECIMAL(12,2),
    ganancia DECIMAL(12,2),
    perdida DECIMAL(12,2),
    progreso DECIMAL(5,2),
    entregables_count INT,
    horas_invertidas INT,
    desviacion_presupuesto DECIMAL(12,2),
    desviacion_tiempo INT,
    tasa_defectos DECIMAL(8,4),
    satisfaccion_cliente DECIMAL(3,2),
    roi DECIMAL(8,2),
    FOREIGN KEY (id_proyecto) REFERENCES Dim_Proyecto(id_proyecto),
    FOREIGN KEY (id_cliente) REFERENCES Dim_Cliente(id_cliente),
    FOREIGN KEY (id_responsable) REFERENCES Dim_Responsable(id_responsable),
    FOREIGN KEY (id_tiempo) REFERENCES Dim_Tiempo(id_tiempo)
);

-- Fact de Tareas
CREATE TABLE IF NOT EXISTS Fact_Tareas (
    id_fact_tarea INT AUTO_INCREMENT PRIMARY KEY,
    id_tarea INT,
    id_proyecto INT,
    id_responsable INT,
    id_tiempo INT,
    horas_estimadas DECIMAL(8,2),
    horas_reales DECIMAL(8,2),
    estado VARCHAR(20),
    desviacion_horas DECIMAL(8,2),
    FOREIGN KEY (id_tarea) REFERENCES Dim_Tarea(id_tarea),
    FOREIGN KEY (id_proyecto) REFERENCES Dim_Proyecto(id_proyecto),
    FOREIGN KEY (id_responsable) REFERENCES Dim_Responsable(id_responsable),
    FOREIGN KEY (id_tiempo) REFERENCES Dim_Tiempo(id_tiempo)
);

-- Fact de Tiempo de Trabajo
CREATE TABLE IF NOT EXISTS Fact_Tiempo_Trabajo (
    id_fact_trabajo INT AUTO_INCREMENT PRIMARY KEY,
    id_responsable INT,
    id_tarea INT,
    id_tiempo INT,
    horas_trabajadas DECIMAL(8,2),
    FOREIGN KEY (id_responsable) REFERENCES Dim_Responsable(id_responsable),
    FOREIGN KEY (id_tarea) REFERENCES Dim_Tarea(id_tarea),
    FOREIGN KEY (id_tiempo) REFERENCES Dim_Tiempo(id_tiempo)
);

-- Fact de Costos
CREATE TABLE IF NOT EXISTS Fact_Costos (
    id_fact_costo INT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT,
    id_tiempo INT,
    tipo VARCHAR(50),
    proveedor VARCHAR(100),
    monto DECIMAL(12,2),
    moneda VARCHAR(10),
    FOREIGN KEY (id_proyecto) REFERENCES Dim_Proyecto(id_proyecto),
    FOREIGN KEY (id_tiempo) REFERENCES Dim_Tiempo(id_tiempo)
);

-- Fact Incidencias
CREATE TABLE IF NOT EXISTS Fact_Incidencias (
    id_fact_incidencia INT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT,
    id_tarea INT,
    id_responsable INT,
    id_tiempo INT,
    severidad VARCHAR(20),
    estado VARCHAR(20),
    dias_resolucion INT,
    FOREIGN KEY (id_proyecto) REFERENCES Dim_Proyecto(id_proyecto),
    FOREIGN KEY (id_tarea) REFERENCES Dim_Tarea(id_tarea),
    FOREIGN KEY (id_responsable) REFERENCES Dim_Responsable(id_responsable),
    FOREIGN KEY (id_tiempo) REFERENCES Dim_Tiempo(id_tiempo)
);

CREATE TABLE IF NOT EXISTS Fact_Defectos (
    id_fact_defecto INT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT,
    id_tiempo INT, -- Fecha de detección
    
    -- Métricas
    cantidad INT DEFAULT 1, 
    tipo_defecto VARCHAR(50),
    severidad VARCHAR(20),
    estado_defecto VARCHAR(20),
    etapa_deteccion VARCHAR(50), 
    dias_correccion INT,
    
    FOREIGN KEY (id_proyecto) REFERENCES Dim_Proyecto(id_proyecto),
    FOREIGN KEY (id_tiempo) REFERENCES Dim_Tiempo(id_tiempo)
);

-- Tabla para almacenar parámetros del modelo Rayleigh
CREATE TABLE IF NOT EXISTS Model_Rayleigh (
    id_model INT AUTO_INCREMENT PRIMARY KEY,
    sigma DECIMAL(10,4) NOT NULL,
    n_samples INT NOT NULL,
    mean_sq DECIMAL(12,4),
    trained_at DATETIME,
    notes TEXT,
    INDEX idx_trained_at (trained_at DESC)
);