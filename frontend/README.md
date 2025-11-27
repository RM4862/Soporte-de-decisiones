# Sistema de Soporte de Decisión - BUAP Software Enterprise

## 📋 Descripción del Proyecto

Sistema de Soporte de Decisión (DSS) diseñado para una empresa de desarrollo de software de egresados de la BUAP. El sistema integra dashboards dinámicos para la visualización de KPIs y OKRs, utilizando un cubo OLAP y Balanced Scorecard, además de un modelo predictivo basado en la distribución de Rayleigh.

## 🎯 Misión y Visión

### Misión
Desarrollar soluciones de software de alta calidad que optimicen los procesos de nuestros clientes mediante la innovación tecnológica, la eficiencia operativa y la mejora continua; ofreciendo productos sostenibles, escalables y alineados con las necesidades de negocio mientras se promueve la trazabilidad, la colaboración interdisciplinaria y el uso ético de los datos.

### Visión
Ser una empresa líder en el desarrollo de software inteligente que impulse la transformación digital a través de soluciones confiables, medibles y centradas en la toma de decisiones basadas en datos. Aspiramos a consolidarnos como un referente en la creación de plataformas donde la analítica de desempeño, la gestión del conocimiento y la automatización se integren para orientar la estrategia empresarial hacia la excelencia y la innovación sostenible.

## 🚀 Características Principales

### 1. Dashboard Principal
- Resumen ejecutivo de indicadores clave de desempeño (KPIs)
- Visualización de proyectos activos, ingresos y satisfacción del cliente
- Gráficos de tendencias y distribución de defectos
- Tabla de proyectos recientes con estado y progreso

### 2. Dashboard OLAP (Online Analytical Processing)
- **Análisis Multidimensional** con 4 dimensiones:
  - Dimensión Temporal: Evolución de ingresos, proyectos y calidad
  - Dimensión Tecnológica: Análisis por tecnologías utilizadas
  - Dimensión Cliente: Segmentación y satisfacción por tipo de cliente
  - Dimensión Calidad: Métricas de cobertura de pruebas y defectos

- **Funcionalidades OLAP:**
  - Drill-down para análisis detallado
  - Agregaciones personalizables (suma, promedio, máximo, mínimo)
  - Filtros por período y métricas
  - Insights automáticos basados en análisis de datos

### 3. Balanced Scorecard
- **4 Perspectivas Estratégicas:**
  1. **Perspectiva Financiera:** ROI, rentabilidad, crecimiento de ingresos
  2. **Perspectiva de Clientes:** Satisfacción, NPS, adquisición y retención
  3. **Perspectiva de Procesos Internos:** Excelencia operativa, innovación
  4. **Perspectiva de Aprendizaje y Crecimiento:** Desarrollo del talento, gestión del conocimiento

- **Visualización de OKRs (Objectives and Key Results):**
  - Objetivos con metas y progreso en tiempo real
  - Key Results específicos para cada objetivo
  - Gráfico radar de rendimiento global
  - Evolución trimestral de cumplimiento
  - Iniciativas estratégicas en curso

### 4. Modelo Predictivo de Defectos (Rayleigh)
- **Acceso Restringido:** Solo para responsables de proyecto
- **Entrada de Parámetros:**
  - Tamaño del proyecto (LOC)
  - Complejidad del proyecto
  - Experiencia del equipo
  - Duración estimada

- **Predicciones Generadas:**
  - Total de defectos estimados
  - Momento del pico de defectos
  - Distribución temporal de defectos (curva de Rayleigh)
  - Defectos acumulados a lo largo del tiempo
  - Distribución por severidad (críticos, mayores, menores, triviales)
  - Nivel de riesgo del proyecto
  - Recomendaciones específicas basadas en la predicción

- **Fundamento Matemático:**
  - Función de densidad de Rayleigh: f(t) = (t / σ²) × e^(−t² / 2σ²)
  - Defectos acumulados: F(t) = Total × (1 − e^(−t² / 2σ²))

## 🛠️ Tecnologías Utilizadas

- **Frontend Framework:** React 18.3
- **Build Tool:** Vite 5.1
- **Routing:** React Router DOM 6.22
- **Styling:** Tailwind CSS 3.4
- **Charts:** Recharts 2.12 (gráficos interactivos y responsivos)
- **Icons:** Lucide React 0.344
- **Utilities:** clsx para gestión de clases CSS

## 📦 Instalación

### Prerrequisitos
- Node.js 18 o superior
- npm o yarn

### Pasos de Instalación

1. Clonar el repositorio:
```bash
cd soporte_decisiones
```

2. Instalar dependencias:
```bash
npm install
```

3. Iniciar el servidor de desarrollo:
```bash
npm run dev
```

4. Abrir el navegador en `http://localhost:3000`

## 📁 Estructura del Proyecto

```
soporte_decisiones/
├── public/
├── src/
│   ├── components/
│   │   ├── Layout.jsx          # Layout principal con sidebar y header
│   │   ├── Sidebar.jsx         # Navegación lateral
│   │   └── Header.jsx          # Barra superior con notificaciones
│   ├── pages/
│   │   ├── Dashboard.jsx       # Dashboard principal con KPIs
│   │   ├── OLAPDashboard.jsx   # Dashboard OLAP multidimensional
│   │   ├── BalancedScorecard.jsx # Balanced Scorecard con OKRs
│   │   └── PredictiveModel.jsx # Modelo predictivo de Rayleigh
│   ├── App.jsx                 # Configuración de rutas
│   ├── main.jsx               # Punto de entrada
│   └── index.css              # Estilos globales
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## 🔐 Autenticación

El modelo predictivo requiere autenticación. Las credenciales por defecto son:
- **Usuario:** admin
- **Contraseña:** admin123

**Nota:** En producción, implementar un sistema de autenticación robusto con backend.

## 📊 Datos del Sistema

Actualmente, el sistema utiliza datos simulados para demostración. Para producción:

### ETL (Extract, Transform, Load)
1. **Extracción:** Conectar con sistema de gestión (base de datos, APIs)
2. **Transformación:** Procesar y limpiar datos, calcular métricas
3. **Carga:** Alimentar el cubo OLAP y dashboards

### Cubo OLAP
- **Dimensiones:** Tiempo, Tecnología, Cliente, Calidad
- **Hechos:** Ingresos, Proyectos, Defectos, Satisfacción
- **Medidas:** Agregaciones (suma, promedio, conteo)

### Integración Recomendada
- **Base de Datos:** PostgreSQL o SQL Server con extensiones OLAP
- **ETL Tool:** Apache Airflow, Pentaho, o Talend
- **Backend API:** Node.js/Express o Python/FastAPI
- **Tiempo Real:** WebSockets para actualizaciones en vivo

## 📈 Modelo Predictivo - Distribución de Rayleigh

### Fundamento Teórico
La distribución de Rayleigh se utiliza ampliamente en ingeniería de software para modelar la curva de ciclo de vida de defectos:

- **Fase Inicial:** Pocos defectos (sistema en construcción)
- **Fase Media:** Pico de defectos (máxima funcionalidad siendo integrada)
- **Fase Final:** Disminución de defectos (estabilización)

### Parámetros del Modelo
- **σ (sigma):** Parámetro de escala que determina la dispersión
- **Tiempo del Pico:** t_peak = σ√2
- **Factores de Ajuste:**
  - Complejidad: 0.8 (baja) a 1.6 (muy alta)
  - Experiencia: 1.4 (baja) a 0.5 (experto)

### Aplicación Práctica
1. Estimar defectos totales basados en tamaño y complejidad
2. Distribuir defectos temporalmente según Rayleigh
3. Identificar momento crítico para reforzar QA
4. Planificar recursos de testing
5. Ajustar modelo con datos reales del proyecto

## 🎨 Personalización

### Colores (tailwind.config.js)
Modificar la paleta de colores primarios en `theme.extend.colors.primary`

### Datos
Reemplazar los datos simulados en cada página con llamadas a API:
```javascript
// Ejemplo
const fetchData = async () => {
  const response = await fetch('/api/kpis')
  const data = await response.json()
  setKpiData(data)
}
```

### Gráficos
Ajustar configuración de Recharts según necesidades:
- Colores, tamaños, leyendas
- Tipos de gráficos (línea, barra, área, radar, etc.)
- Tooltips personalizados

## 📋 Comandos Disponibles

- `npm run dev` - Iniciar servidor de desarrollo
- `npm run build` - Construir para producción
- `npm run preview` - Previsualizar build de producción

## 🔒 Certificación y Documentación

### Proceso ETL Documentado
1. **Fuentes de Datos:** Sistema de gestión de proyectos, repositorios Git, sistema de tracking de defectos
2. **Frecuencia:** Actualización diaria o en tiempo real
3. **Transformaciones:** Cálculos de KPIs, agregaciones OLAP, normalización de datos
4. **Validación:** Checks de calidad de datos, manejo de valores nulos, detección de anomalías

### Modelo de Madurez
El sistema está diseñado para cumplir con modelos de madurez como CMMI:
- **Nivel 2 (Gestionado):** Procesos documentados y repetibles
- **Nivel 3 (Definido):** Procesos estandarizados y coherentes
- **Nivel 4 (Cuantitativamente Gestionado):** Medición y control estadístico (DSS actual)
- **Nivel 5 (Optimizado):** Mejora continua basada en analítica predictiva

### Documentación Técnica
- README.md: Descripción general y guía de instalación
- Código comentado: Explicaciones en línea de lógica compleja
- Diagramas de arquitectura: (Recomendado añadir)
- Manual de usuario: (Recomendado crear)
- Guía de mantenimiento: (Recomendado crear)

## 🚧 Roadmap Futuro

### Fase 1 - MVP Actual ✅
- Dashboard principal con KPIs
- Dashboard OLAP multidimensional
- Balanced Scorecard con OKRs
- Modelo predictivo de Rayleigh

### Fase 2 - Backend e Integración
- [ ] API REST para datos dinámicos
- [ ] Autenticación JWT robusta
- [ ] Integración con sistema de gestión
- [ ] Pipeline ETL automatizado

### Fase 3 - Analítica Avanzada
- [ ] Machine Learning para predicciones mejoradas
- [ ] Alertas automáticas basadas en umbrales
- [ ] Exportación de reportes (PDF, Excel)
- [ ] Dashboards personalizables por usuario

### Fase 4 - Optimización
- [ ] Cache de datos para rendimiento
- [ ] Actualizaciones en tiempo real (WebSockets)
- [ ] Pruebas unitarias e integración
- [ ] CI/CD pipeline

## 👥 Contribuciones

Para contribuir al proyecto:
1. Fork el repositorio
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está desarrollado como parte del trabajo académico de la BUAP.

## 📞 Contacto

BUAP Software Enterprise - Equipo de Desarrollo

---

**Desarrollado con ❤️ por estudiantes de la BUAP**
