# Modelo Predictivo Rayleigh - Documentación

## Descripción General

Este sistema implementa un modelo predictivo basado en la distribución Rayleigh para predecir defectos en proyectos de software usando **etapas del ciclo de vida como tiempo**.

### Concepto Clave: Etapas como Tiempo

En lugar de usar tiempo calendario, el modelo usa las **etapas del proyecto** como eje temporal:

1. **Inicio** (t=1)
2. **Planificación** (t=2)
3. **Ejecución** (t=3) ← Pico de defectos
4. **Monitoreo y Control** (t=4)
5. **Cierre** (t=5)

La distribución Rayleigh modela cómo los defectos se concentran en la etapa de **Ejecución** y disminuyen hacia el inicio y cierre del proyecto.

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    SG_Proyectos (MySQL)                 │
│  ┌──────────────┐      ┌────────────────────────────┐  │
│  │  Proyectos   │      │       Defectos             │  │
│  │              │◄─────┤  - etapa_deteccion         │  │
│  │  - id        │      │  - tipo_defecto            │  │
│  │  - nombre    │      │  - severidad               │  │
│  │  - estado    │      │  - fecha_deteccion         │  │
│  └──────────────┘      └────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            │ Query por etapa
                            ▼
┌─────────────────────────────────────────────────────────┐
│              train_rayleigh.py                          │
│  - Extrae defectos agrupados por etapa                  │
│  - Ajusta modelo Rayleigh (MLE)                         │
│  - Guarda rayleigh_model.json                           │
│  - Persiste en DSS_Proyectos.Model_Rayleigh             │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              rayleigh_api.py (Flask)                    │
│  Endpoints:                                             │
│  - POST /predict → Predicción desde modelo guardado     │
│  - POST /predict_filtered → Predicción con filtros      │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Frontend (React)                           │
│  - PredictiveModel.jsx                                  │
│  - Visualización de curva Rayleigh                      │
│  - Filtros interactivos                                 │
└─────────────────────────────────────────────────────────┘
```

## Query Principal

El modelo se entrena con el siguiente query que agrupa defectos por etapa:

```sql
SELECT 
    d.etapa_deteccion AS Etapa,
    SUM(CASE WHEN p.id_proyecto = (SELECT id_proyecto FROM Proyectos LIMIT 1 OFFSET 0) THEN 1 ELSE 0 END) AS Proyecto_A,
    SUM(CASE WHEN p.id_proyecto = (SELECT id_proyecto FROM Proyectos LIMIT 1 OFFSET 1) THEN 1 ELSE 0 END) AS Proyecto_B,
    SUM(CASE WHEN p.id_proyecto = (SELECT id_proyecto FROM Proyectos LIMIT 1 OFFSET 2) THEN 1 ELSE 0 END) AS Proyecto_C,
    SUM(CASE WHEN p.id_proyecto = (SELECT id_proyecto FROM Proyectos LIMIT 1 OFFSET 3) THEN 1 ELSE 0 END) AS Proyecto_D,
    SUM(CASE WHEN p.id_proyecto = (SELECT id_proyecto FROM Proyectos LIMIT 1 OFFSET 4) THEN 1 ELSE 0 END) AS Proyecto_E
FROM 
    Defectos d
JOIN 
    Proyectos p ON d.id_proyecto = p.id_proyecto
WHERE 
    d.etapa_deteccion IS NOT NULL
GROUP BY 
    d.etapa_deteccion
ORDER BY 
    FIELD(d.etapa_deteccion, 'Inicio', 'Planificación', 'Ejecución', 'Monitoreo y Control', 'Cierre');
```

## Instalación y Configuración

### 1. Dependencias Python

```bash
cd backend
pip install flask mysql-connector-python faker
```

### 2. Configuración de Base de Datos

Las credenciales se pueden configurar con variables de entorno o usar los valores por defecto:

```bash
# Para SG_Proyectos (base de datos operacional)
set SG_HOST=localhost
set SG_USER=root
set SG_PASSWORD=
set SG_DATABASE=SG_Proyectos

# Para DSS_Proyectos (data warehouse)
set DW_HOST=localhost
set DW_USER=root
set DW_PASSWORD=
set DW_DATABASE=DSS_Proyectos
```

### 3. Generar Datos de Prueba

```bash
python "generar_datos (1).py"
```

Esto genera:
- 15 clientes
- 12 responsables
- 25 proyectos
- 350 defectos distribuidos por etapa (siguiendo distribución Rayleigh)
- Otros datos relacionados

### 4. Entrenar el Modelo

```bash
python train_rayleigh.py
```

Salida esperada:
```
Conectando a SG_Proyectos para obtener defectos por etapa...
Muestras obtenidas: 5 etapas (tiempo)
Modelo guardado en rayleigh_model.json
Persistiendo parámetros en DW (Model_Rayleigh)...
Persistencia en DW completada.
Resumen del modelo:
{
  "sigma": 9.39,
  "n_samples": 5,
  "expected": 11.77,
  "p90": 20.16,
  "trained_at": "2025-11-27T..."
}
```

### 5. Iniciar el API

```bash
python rayleigh_api.py
```

El servidor estará disponible en `http://localhost:5000`

## Uso del API

### Endpoint: POST /predict

Devuelve predicción basada en el modelo entrenado.

**Request:**
```json
{
  "auth_key": "changeme",
  "round": 2
}
```

**Response:**
```json
{
  "sigma": 9.39,
  "n_samples": 5,
  "expected_defects": 11.77,
  "p90": 20.16,
  "trained_at": "2025-11-27T..."
}
```

### Endpoint: POST /predict_filtered

Aplica filtros y ajusta el modelo dinámicamente.

**Request:**
```json
{
  "auth_key": "changeme",
  "filters": {
    "etapas": ["Ejecución", "Monitoreo y Control"],
    "metodologia": "Scrum",
    "estado": "En progreso"
  }
}
```

**Response:**
```json
{
  "sigma": 8.5,
  "n_samples": 3,
  "expected_defects": 10.65,
  "p90": 18.22,
  "etapas": [
    {
      "etapa": "Ejecución",
      "tiempo": 3,
      "defectos": 45
    },
    {
      "etapa": "Monitoreo y Control",
      "tiempo": 4,
      "defectos": 30
    }
  ],
  "note": "Etapas usadas como tiempo: 1=Inicio, 2=Planificación, 3=Ejecución, 4=Monitoreo y Control, 5=Cierre"
}
```

## Filtros Disponibles

- `etapas`: Lista de etapas a incluir (ej: `["Inicio", "Planificación"]`)
- `metodologia`: Filtrar por metodología (ej: `"Scrum"`, `"Waterfall"`)
- `estado`: Estado del proyecto (ej: `"En progreso"`, `"Completado"`)
- `fecha_inicio_min`: Fecha mínima de inicio (formato: `YYYY-MM-DD`)
- `fecha_inicio_max`: Fecha máxima de inicio

## Interpretación de Resultados

### Parámetros del Modelo

- **sigma (σ)**: Parámetro de escala de la distribución Rayleigh. Mayor valor = mayor dispersión de defectos
- **n_samples**: Número de etapas/períodos usados para entrenar
- **expected_defects**: Valor esperado (promedio) de defectos = σ × √(π/2) ≈ 1.253 × σ
- **p90**: Percentil 90. Hay 90% de probabilidad de que los defectos estén por debajo de este valor

### Ejemplo de Interpretación

Si el modelo devuelve:
```json
{
  "sigma": 9.39,
  "expected_defects": 11.77,
  "p90": 20.16
}
```

**Significa:**
- En promedio, se esperan **11.77 defectos** por etapa
- El pico de defectos ocurre en la **etapa de Ejecución** (t=3)
- Hay 90% de confianza de que los defectos no excedan **20.16** por etapa

## Estructura de Archivos

```
backend/
├── rayleigh_model.py          # Funciones matemáticas de Rayleigh
├── train_rayleigh.py          # Script de entrenamiento
├── rayleigh_api.py            # API Flask
├── rayleigh_model.json        # Modelo entrenado (generado)
├── generar_datos (1).py       # Generador de datos de prueba
├── test_rayleigh_api.py       # Tests del API
└── README_RAYLEIGH.md         # Esta documentación
```

## Fórmulas Matemáticas

### Distribución Rayleigh

**PDF (Función de Densidad):**
```
f(x; σ) = (x / σ²) × exp(-x² / (2σ²))
```

**CDF (Función de Distribución Acumulada):**
```
F(x; σ) = 1 - exp(-x² / (2σ²))
```

**Estimador MLE para σ:**
```
σ̂ = √((1/2n) × Σx²)
```

**Valor Esperado:**
```
E[X] = σ × √(π/2) ≈ 1.253 × σ
```

**Percentil p:**
```
q(p) = σ × √(-2 × ln(1-p))
```

## Seguridad

⚠️ **Importante para Producción:**

1. Cambiar `RESP_KEY` de `"changeme"` a un valor seguro
2. Usar variables de entorno para todas las credenciales
3. Implementar HTTPS
4. Considerar autenticación OAuth2 o JWT
5. Validar y sanitizar todos los inputs

## Solución de Problemas

### Error: "Table 'dss_proyectos.model_rayleigh' doesn't exist"

**Solución:**
```sql
USE DSS_Proyectos;
CREATE TABLE IF NOT EXISTS Model_Rayleigh (
    id_model INT AUTO_INCREMENT PRIMARY KEY,
    sigma DECIMAL(10,4) NOT NULL,
    n_samples INT NOT NULL,
    mean_sq DECIMAL(12,4),
    trained_at DATETIME,
    notes TEXT,
    INDEX idx_trained_at (trained_at DESC)
);
```

### Error: "No hay datos para entrenar"

Verifica que existan defectos con `etapa_deteccion` no nulo:
```sql
SELECT etapa_deteccion, COUNT(*) 
FROM Defectos 
WHERE etapa_deteccion IS NOT NULL 
GROUP BY etapa_deteccion;
```

### API no responde

Verifica que el servidor esté corriendo:
```bash
python rayleigh_api.py
```

Debe mostrar:
```
 * Running on http://0.0.0.0:5000
```

## Referencias

- Putnam, L. H. (1978). "A General Empirical Solution to the Macro Software Sizing and Estimating Problem"
- Rayleigh Distribution: https://en.wikipedia.org/wiki/Rayleigh_distribution
- Software Reliability Growth Models: IEEE Standards
