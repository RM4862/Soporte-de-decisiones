# 🔐 Variables de Entorno para Render

## 📋 Lista Completa de Variables

### 🔴 BACKEND API (Obligatorias)

Configura estas en el servicio **backend** en Render:

```
SG_HOST=tu_host_mysql_aqui
SG_USER=tu_usuario_mysql
SG_PASSWORD=tu_contraseña_mysql_segura
SG_DATABASE=SG_Proyectos

DW_HOST=tu_host_mysql_aqui
DW_USER=tu_usuario_mysql
DW_PASSWORD=tu_contraseña_mysql_segura
DW_DATABASE=DSS_Proyectos

MODEL_FILE=rayleigh_model.json
RESP_KEY=clave_secreta_minimo_32_caracteres
PYTHONUNBUFFERED=1
```

### 🟢 FRONTEND (Obligatoria)

Configura esta en el servicio **frontend** en Render:

```
VITE_API_URL=https://TU-NOMBRE-API.onrender.com
```

---

## 📝 Cómo Obtener los Valores

### 1. **Base de Datos MySQL** (SG_HOST, SG_USER, SG_PASSWORD)

#### Opción A: PlanetScale (Gratis, Recomendado)
1. Ve a [planetscale.com](https://planetscale.com)
2. Crea cuenta y nueva base de datos
3. Obtén el connection string:
   - Host: `xxx.planetscale.net`
   - User: `xxx`
   - Password: `pscale_pw_xxxxx`

#### Opción B: Railway (Gratis con límites)
1. Ve a [railway.app](https://railway.app)
2. New Project → MySQL
3. Variables disponibles en el panel

#### Opción C: Render MySQL ($7/mes)
1. En Render: New → MySQL
2. Copia el "Internal Connection String"
3. Formato: `mysql://user:password@host/database`

### 2. **RESP_KEY** (Clave de seguridad API)

Genera una clave segura de 32+ caracteres:

**PowerShell:**
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

**Linux/Mac:**
```bash
openssl rand -base64 32
```

**Online:**
[random.org/strings](https://www.random.org/strings/?num=1&len=32&digits=on&upperalpha=on&loweralpha=on)

Ejemplo: `aB3xK9mP2qR7sT1wV4yZ8nL6jH5cF0dG`

### 3. **VITE_API_URL** (URL del Backend)

Después de desplegar el backend, obtendrás una URL como:
```
https://soporte-decisiones-api.onrender.com
```

Úsala tal cual (sin `/` al final).

---

## 🎯 Ejemplo Completo con Valores Reales

### Backend API:
```
SG_HOST=aws.connect.psdb.cloud
SG_USER=r2d2x9k0m1p2q3r4
SG_PASSWORD=pscale_pw_a1b2c3d4e5f6g7h8i9j0
SG_DATABASE=SG_Proyectos

DW_HOST=aws.connect.psdb.cloud
DW_USER=r2d2x9k0m1p2q3r4
DW_PASSWORD=pscale_pw_a1b2c3d4e5f6g7h8i9j0
DW_DATABASE=DSS_Proyectos

MODEL_FILE=rayleigh_model.json
RESP_KEY=k9L2mN4pQ7rS1tV3wX6yZ8aB0cD5eF9gH
PYTHONUNBUFFERED=1
```

### Frontend:
```
VITE_API_URL=https://soporte-decisiones-api.onrender.com
```

---

## ⚠️ Notas Importantes

1. **Mismas credenciales para SG y DW**: Si ambas bases de datos están en el mismo servidor MySQL, usa los mismos valores de `HOST`, `USER` y `PASSWORD`.

2. **No uses localhost**: En Render debes usar el host externo de tu base de datos, nunca `localhost`.

3. **Crea las bases de datos**: Asegúrate de crear `SG_Proyectos` y `DSS_Proyectos` en tu servidor MySQL antes de desplegar.

4. **RESP_KEY única**: No uses `changeme`, genera una clave única y segura.

5. **Sin espacios ni comillas**: En Render, escribe los valores directamente sin comillas:
   ```
   ✅ Correcto: SG_HOST=aws.connect.psdb.cloud
   ❌ Incorrecto: SG_HOST="aws.connect.psdb.cloud"
   ```

---

## 🚀 Configuración en Render (Paso a Paso)

### Backend:
1. Ve a tu servicio backend en Render
2. Click en **"Environment"** en el menú lateral
3. Click en **"Add Environment Variable"**
4. Agrega cada variable una por una
5. Click en **"Save Changes"**

### Frontend:
1. Ve a tu servicio frontend en Render
2. Click en **"Environment"**
3. Agrega solo `VITE_API_URL`
4. El valor debe ser la URL de tu backend (cópiala del servicio backend)

---

## 🧪 Verificar Configuración

Después de configurar, prueba:

**Backend Health Check:**
```
https://TU-BACKEND.onrender.com/api/dashboard/summary
```

Debe devolver JSON con datos del dashboard.

**Frontend:**
```
https://TU-FRONTEND.onrender.com
```

Debe cargar la aplicación y conectarse al backend.
