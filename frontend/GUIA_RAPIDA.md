# 🚀 Guía Rápida de Inicio

## Inicio Rápido en 3 Pasos

### 1️⃣ Instalar Dependencias
```bash
npm install
```

### 2️⃣ Iniciar el Servidor de Desarrollo
```bash
npm run dev
```

### 3️⃣ Abrir en el Navegador
Navega a: **http://localhost:3000**

---

## 🎯 Navegación de la Aplicación

### Dashboard Principal
**Ruta:** `/`

Muestra una vista ejecutiva con:
- 4 tarjetas de KPIs principales
- Gráfico de proyectos por mes
- Distribución de defectos
- Tabla de proyectos recientes

### OLAP Analytics
**Ruta:** `/olap`

Dashboard interactivo con análisis multidimensional:
- **4 Dimensiones de Análisis:**
  - ⏰ Temporal (evolución en el tiempo)
  - 💻 Tecnológica (por tecnologías)
  - 👥 Cliente (por segmento)
  - ✅ Calidad (métricas de calidad)

**Características:**
- Filtros dinámicos por dimensión, métrica y período
- Drill-down para análisis detallado
- Insights automáticos generados
- Exportación de datos

### Balanced Scorecard
**Ruta:** `/balanced-scorecard`

Visualización de OKRs en 4 perspectivas:
1. 💰 **Financiera** - Rentabilidad y crecimiento
2. 🎯 **Clientes** - Satisfacción y adquisición
3. ⚙️ **Procesos Internos** - Excelencia e innovación
4. 📚 **Aprendizaje** - Desarrollo y conocimiento

**Características:**
- Gráfico radar de rendimiento global
- Progreso de objetivos con Key Results
- Iniciativas estratégicas en curso
- Identificación de fortalezas y áreas de mejora

### Modelo Predictivo
**Ruta:** `/predictive-model`

Predicción de defectos usando distribución de Rayleigh:
- 🔒 **Acceso restringido** a responsables de proyecto
- Credenciales de prueba: `admin123`

**Parámetros de Entrada:**
- Tamaño del proyecto (LOC)
- Complejidad
- Experiencia del equipo
- Duración estimada

**Resultados Generados:**
- Total de defectos estimados
- Momento del pico de defectos
- Curva de Rayleigh con defectos acumulados
- Distribución por severidad
- Nivel de riesgo del proyecto
- Recomendaciones específicas

---

## 🎨 Personalización Rápida

### Cambiar Colores
Editar `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Cambiar estos valores
        500: '#0ea5e9',
        600: '#0284c7',
        700: '#0369a1',
      },
    },
  },
}
```

### Actualizar Logo/Nombre
Editar `src/components/Sidebar.jsx`:
```jsx
<div className="text-white">
  <div className="font-bold text-lg">TU NOMBRE</div>
  <div className="text-xs">TU SUBTÍTULO</div>
</div>
```

### Modificar Datos
Los datos simulados están en cada página:
- `src/pages/Dashboard.jsx` - Datos del dashboard principal
- `src/pages/OLAPDashboard.jsx` - Datos del cubo OLAP
- `src/pages/BalancedScorecard.jsx` - Datos de OKRs
- `src/pages/PredictiveModel.jsx` - Lógica del modelo

---

## 📊 Conectar con API Real

### Paso 1: Crear Servicio API
```javascript
// src/services/api.js
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000/api'

export const fetchKPIs = async () => {
  const response = await fetch(`${API_BASE_URL}/kpis`)
  return response.json()
}

export const fetchOLAPData = async (dimension, metric) => {
  const response = await fetch(
    `${API_BASE_URL}/olap?dimension=${dimension}&metric=${metric}`
  )
  return response.json()
}
```

### Paso 2: Usar en Componentes
```javascript
// src/pages/Dashboard.jsx
import { fetchKPIs } from '../services/api'
import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [kpiData, setKpiData] = useState([])
  
  useEffect(() => {
    const loadData = async () => {
      const data = await fetchKPIs()
      setKpiData(data)
    }
    loadData()
  }, [])
  
  // ... resto del componente
}
```

### Paso 3: Variables de Entorno
Crear archivo `.env`:
```
VITE_API_URL=http://localhost:8000/api
```

---

## 🏗️ Build para Producción

### Crear Build Optimizado
```bash
npm run build
```

Esto generará una carpeta `dist/` con los archivos optimizados.

### Previsualizar Build
```bash
npm run preview
```

### Deploy (Ejemplos)

#### Vercel
```bash
npm install -g vercel
vercel --prod
```

#### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod
```

#### Servidor Propio (Nginx)
```nginx
server {
    listen 80;
    server_name dss.tuempresa.com;
    root /var/www/dss/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 🔧 Comandos Útiles

```bash
# Desarrollo
npm run dev              # Iniciar servidor de desarrollo

# Build
npm run build            # Crear build de producción
npm run preview          # Previsualizar build

# Herramientas
npm run lint             # Ejecutar linter (si está configurado)
npm run format           # Formatear código (si está configurado)
```

---

## 📱 Responsive Design

La aplicación está completamente optimizada para:
- 📱 **Móviles** (320px+)
- 📱 **Tablets** (768px+)
- 💻 **Desktop** (1024px+)
- 🖥️ **Large Desktop** (1280px+)

### Breakpoints de Tailwind
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

---

## 🐛 Solución de Problemas Comunes

### Error: "Cannot find module..."
**Solución:** Reinstalar dependencias
```bash
rm -rf node_modules package-lock.json
npm install
```

### Puerto 3000 ya en uso
**Solución 1:** Cambiar puerto en `vite.config.js`
```javascript
server: {
  port: 3001
}
```

**Solución 2:** Terminar proceso en puerto 3000
```bash
# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process

# Linux/Mac
lsof -ti:3000 | xargs kill
```

### Estilos de Tailwind no se aplican
**Solución:** Verificar que `index.css` esté importado en `main.jsx`
```javascript
import './index.css'
```

### Gráficos no se muestran
**Solución:** Verificar importación de Recharts
```javascript
import { LineChart, Line, ... } from 'recharts'
```

---

## 📚 Recursos Adicionales

### Documentación
- [README.md](README.md) - Documentación completa del proyecto
- [DOCUMENTACION_PROCESOS.md](DOCUMENTACION_PROCESOS.md) - ETL, OLAP, y procesos

### Tecnologías
- [React](https://react.dev) - Framework UI
- [Vite](https://vitejs.dev) - Build tool
- [Tailwind CSS](https://tailwindcss.com) - Estilos
- [Recharts](https://recharts.org) - Gráficos
- [React Router](https://reactrouter.com) - Navegación
- [Lucide Icons](https://lucide.dev) - Iconos

### Aprende Más
- [Tutorial de React](https://react.dev/learn)
- [Guía de Tailwind](https://tailwindcss.com/docs)
- [Ejemplos de Recharts](https://recharts.org/en-US/examples)

---

## 💡 Tips y Mejores Prácticas

### 1. Organización de Código
- Mantén componentes pequeños y reutilizables
- Usa hooks personalizados para lógica compartida
- Separa lógica de negocio de presentación

### 2. Performance
- Usa `React.memo` para componentes pesados
- Implementa lazy loading para rutas
- Optimiza imágenes y assets

### 3. Testing (Recomendado añadir)
```bash
npm install --save-dev @testing-library/react vitest
```

### 4. Git Workflow
```bash
# Crear rama de feature
git checkout -b feature/nueva-funcionalidad

# Commit con mensaje descriptivo
git commit -m "feat: agregar filtro por fecha en OLAP"

# Push y crear PR
git push origin feature/nueva-funcionalidad
```

---

## 🎯 Checklist de Producción

Antes de desplegar a producción:

- [ ] Probar en múltiples navegadores (Chrome, Firefox, Safari, Edge)
- [ ] Validar responsive en diferentes dispositivos
- [ ] Verificar accesibilidad (a11y)
- [ ] Optimizar imágenes y assets
- [ ] Configurar variables de entorno de producción
- [ ] Implementar analytics (Google Analytics, Mixpanel, etc.)
- [ ] Configurar manejo de errores (Sentry, LogRocket, etc.)
- [ ] Añadir tests automatizados
- [ ] Documentar APIs y componentes
- [ ] Configurar CI/CD pipeline
- [ ] Implementar autenticación real (JWT, OAuth)
- [ ] Añadir SSL/HTTPS
- [ ] Configurar backups automáticos

---

## 🆘 Soporte

¿Problemas o preguntas?

1. Revisar [README.md](README.md) y [DOCUMENTACION_PROCESOS.md](DOCUMENTACION_PROCESOS.md)
2. Buscar en los issues de GitHub
3. Contactar al equipo de desarrollo

---

**¡Feliz desarrollo! 🎉**

*Actualizado: Noviembre 2024*
