# 🚀 Guía de Despliegue en Render

## 📋 Requisitos Previos

1. **Cuenta en Render**: [render.com](https://render.com)
2. **Base de datos MySQL externa**: PlanetScale, Railway, o Render MySQL
3. **Repositorio en GitHub**: Tu código debe estar subido

---

## 🔧 Configuración Paso a Paso

### 1️⃣ Preparar Base de Datos MySQL

**Opción A: PlanetScale (Recomendado - Gratis)**
```bash
# Crear cuenta en planetscale.com
# Crear nueva base de datos
# Obtener Connection String
```

**Opción B: Render MySQL**
```bash
# En Render Dashboard > New > MySQL
# Nombre: soporte-decisiones-db
# Copiar Internal Connection String
```

### 2️⃣ Conectar Repositorio a Render

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click en **"New"** > **"Blueprint"**
3. Conecta tu repositorio de GitHub: `RM4862/Soporte-de-decisiones`
4. Render detectará automáticamente el archivo `render.yaml`

### 3️⃣ Configurar Variables de Entorno

En cada servicio (API y Frontend), configura:

#### 🔴 Backend API - Variables Obligatorias:

```bash
SG_HOST=tu_mysql_host.planetscale.net
SG_USER=tu_usuario
SG_PASSWORD=tu_password_segura
SG_DATABASE=SG_Proyectos

DW_HOST=tu_mysql_host.planetscale.net
DW_USER=tu_usuario
DW_PASSWORD=tu_password_segura
DW_DATABASE=DSS_Proyectos

RESP_KEY=tu_clave_secreta_32_caracteres_minimo
```

#### Generar RESP_KEY segura (PowerShell):
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

### 4️⃣ Inicializar Base de Datos

Una vez desplegado el backend, conéctate a tu MySQL y ejecuta:

```bash
# 1. Conectar a tu MySQL
mysql -h tu_host -u tu_usuario -p

# 2. Ejecutar scripts SQL
source backend/SG_proyectos\ (2).sql
source backend/DSS_proyectos\ (2).sql

# 3. Generar datos (ejecutar desde terminal local)
python backend/generar_datos\ (1).py

# 4. Ejecutar ETL
python backend/etl.py

# 5. Entrenar modelo
python backend/train_rayleigh.py
```

### 5️⃣ Actualizar Frontend con URL del Backend

En `frontend/src/` actualiza las URLs de API con la URL de tu backend en Render:

```javascript
const API_URL = 'https://soporte-decisiones-api.onrender.com';
```

### 6️⃣ Desplegar

```bash
git add .
git commit -m "Configurar para Render"
git push origin master
```

Render desplegará automáticamente ambos servicios.

---

## 🌐 URLs de Acceso

- **Frontend**: `https://soporte-decisiones-frontend.onrender.com`
- **Backend API**: `https://soporte-decisiones-api.onrender.com`
- **API Health Check**: `https://soporte-decisiones-api.onrender.com/api/dashboard/summary`

---

## 🐛 Solución de Problemas

### Error: "Connection refused"
- Verifica que las variables de entorno estén correctamente configuradas
- Revisa los logs en Render Dashboard

### Error: "Table doesn't exist"
- Ejecuta los scripts SQL en tu base de datos MySQL
- Verifica que los nombres de las bases coincidan (SG_Proyectos, DSS_Proyectos)

### Backend tarda en responder
- Render free tier tiene "cold starts" (15-30 segundos en primera carga)
- Considera usar un plan pagado o mantener activo con un cron job

---

## 📞 Soporte

Para más ayuda, revisa:
- [Documentación de Render](https://render.com/docs)
- [Logs en Render Dashboard](https://dashboard.render.com)
