DROP DATABASE IF EXISTS `SG_Proyectos`;
CREATE DATABASE `SG_Proyectos`;
USE `SG_Proyectos`;

-- 1. Clientes
CREATE TABLE Clientes (
  id_cliente INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100), sector VARCHAR(50), pais VARCHAR(50), 
  contacto_nombre VARCHAR(100), contacto_email VARCHAR(100)
);

-- 2. Responsables
CREATE TABLE Responsables (
  id_responsable INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100), rol VARCHAR(50), equipo_asignado VARCHAR(100), 
  correo VARCHAR(100), telefono VARCHAR(50)
);

-- 3. Proyectos
CREATE TABLE Proyectos (
  id_proyecto INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100), descripcion TEXT, metodologia VARCHAR(100),
  fecha_inicio DATE, fecha_fin DATE, presupuesto DECIMAL(12,2),
  costo_total DECIMAL(12,2), ganancia DECIMAL(12,2), perdida DECIMAL(12,2),
  horas_invertidas INT, progreso DECIMAL(5,2), entregables_count INT,
  etapas VARCHAR(100), cronograma TEXT, documentacion TEXT,
  id_cliente INT, id_responsable INT,
  num_tecnologias_emergentes INT DEFAULT 0,
  estado VARCHAR(50) DEFAULT 'Planificación',
  defectos_detectados INT DEFAULT 0,
  FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
  FOREIGN KEY (id_responsable) REFERENCES Responsables(id_responsable)
);

-- 4. Tareas
CREATE TABLE Tareas (
  id_tarea INT AUTO_INCREMENT PRIMARY KEY,
  id_proyecto INT, titulo VARCHAR(100), descripcion TEXT,
  estado ENUM('Pendiente','En progreso','Completada'),
  prioridad ENUM('Alta','Media','Baja'),
  horas_estimadas DECIMAL(8,2), horas_reales DECIMAL(8,2),
  fecha_inicio DATE, fecha_fin DATE,
  FOREIGN KEY (id_proyecto) REFERENCES Proyectos(id_proyecto)
);

-- 5. Registro_Tiempo
CREATE TABLE Registro_Tiempo (
  id_registro INT AUTO_INCREMENT PRIMARY KEY,
  id_responsable INT, id_tarea INT, fecha DATE,
  descripcion TEXT, horasTrabajadas TIME,
  FOREIGN KEY (id_responsable) REFERENCES Responsables(id_responsable),
  FOREIGN KEY (id_tarea) REFERENCES Tareas(id_tarea)
);

-- 6. Costos
CREATE TABLE Costos (
  id_costo INT AUTO_INCREMENT PRIMARY KEY,
  id_proyecto INT, tipo ENUM('Licencia','Infraestructura','Consultoría','Otro'),
  proveedor VARCHAR(100), monto DECIMAL(12,2), moneda VARCHAR(10), fecha DATE,
  FOREIGN KEY (id_proyecto) REFERENCES Proyectos(id_proyecto)
);

-- 7. Incidencias
CREATE TABLE Incidencias (
  id_incidencia INT AUTO_INCREMENT PRIMARY KEY,
  id_proyecto INT, id_tarea INT, id_responsable INT,
  severidad ENUM('Baja','Media','Alta','Crítica'),
  estado ENUM('Abierto','En progreso','Resuelto','Cerrado'),
  fecha_reporte DATE, fecha_resolucion DATE, notas TEXT,
  FOREIGN KEY (id_proyecto) REFERENCES Proyectos(id_proyecto),
  FOREIGN KEY (id_tarea) REFERENCES Tareas(id_tarea),
  FOREIGN KEY (id_responsable) REFERENCES Responsables(id_responsable)
);

-- 8. Capacitaciones
CREATE TABLE Capacitaciones (
  id_capacitacion INT AUTO_INCREMENT PRIMARY KEY,
  id_responsable INT, tema VARCHAR(200), horas DECIMAL(8,2),
  fecha DATE, certificado BOOLEAN,
  FOREIGN KEY (id_responsable) REFERENCES Responsables(id_responsable)
);

-- 9. Tecnologias
CREATE TABLE Tecnologias_Proyecto (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_proyecto INT, tecnologia VARCHAR(100),
  es_emergente BOOLEAN, version VARCHAR(50),
  FOREIGN KEY (id_proyecto) REFERENCES Proyectos(id_proyecto)
);

-- 10. Evaluaciones
CREATE TABLE Evaluaciones_Cliente (
  id_evaluacion INT AUTO_INCREMENT PRIMARY KEY,
  id_proyecto INT, calificacion DECIMAL(3,2),
  comentarios TEXT, fecha DATE,
  FOREIGN KEY (id_proyecto) REFERENCES Proyectos(id_proyecto)
);

-- 11. DEFECTOS 
CREATE TABLE Defectos (
  id_defecto INT AUTO_INCREMENT PRIMARY KEY,
  id_proyecto INT,
  tipo_defecto ENUM('Funcional', 'Interfaz', 'Seguridad', 'Rendimiento', 'Datos'),
  severidad ENUM('Cosmético', 'Menor', 'Mayor', 'Crítico'),
  estado ENUM('Abierto', 'Corregido', 'Rechazado'),
  etapa_deteccion VARCHAR(50),
  fecha_deteccion DATE,
  fecha_correccion DATE,
  FOREIGN KEY (id_proyecto) REFERENCES Proyectos(id_proyecto)
);