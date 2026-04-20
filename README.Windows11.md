# Guía de Despliegue en Windows 11 - TicketsCofat

## Tabla de Contenidos

1. [Prerequisites y Configuración](#prerequisites-y-configuración)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Configuración del Backend](#configuración-del-backend)
4. [Configuración del Frontend](#configuración-del-frontend)
5. [Configuración de IIS](#configuración-de-iis)
6. [Configuración de Firewall](#configuración-de-firewall)
7. [Servicios con Windows Services](#servicios-con-windows-services)
8. [Verificación y Debugging](#verificación-y-debugging)
9. [HTTPS con Certificado (Opcional)](#https-con-certificado-opcional)
10. [Despliegues Futuros](#despliegues-futuros)

---

## Prerequisites y Configuración

### Configurar Windows 11

- **Sistema Operativo**: Windows 11 Pro o Enterprise
- **Hardware**: Mínimo 4GB RAM, 20GB espacio libre
- **Usuario**: Administrador local

### Instalar Chocolatey (Gestor de Paquetes)

Abre PowerShell como administrador y ejecuta:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```

---

## Instalación de Dependencias

### Instalar Python

```powershell
choco install python -y
```

### Instalar Node.js

```powershell
choco install nodejs -y
```

### Instalar IIS (Servidor Web)

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole, IIS-WebServer, IIS-CommonHttpFeatures, IIS-HttpErrors, IIS-HttpLogging, IIS-RequestFiltering, IIS-StaticContent, IIS-CGI
```

### Instalar Git

```powershell
choco install git -y
```

---

## Configuración del Backend

### 1. Clonar o Descargar el Repositorio

```powershell
cd C:\Users\<TuUsuario>\Documents
git clone <tu-repo-url> TicketsCofat
# O si ya está descargado:
cd TicketsCofat
```

### 2. Crear Variables de Entorno (.env)

Crea `C:\Users\<TuUsuario>\Documents\TicketsCofat\.env` con:

```
DJANGO_SECRET_KEY=tu_secreto_largo_aqui_cambiar_en_produccion
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,<TU_IP_LOCAL>
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@example.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=tu-email@example.com
```

### 3. Crear Entorno Virtual e Instalar Dependencias

```powershell
cd C:\Users\<TuUsuario>\Documents\TicketsCofat
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install waitress
```

### 4. Ejecutar Migraciones de Base de Datos

```powershell
set DJANGO_SETTINGS_MODULE=tickets.settings
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Crear Superusuario (Opcional)

```powershell
python manage.py createsuperuser
```

---

## Configuración del Frontend

### 1. Instalar Dependencias

```powershell
cd C:\Users\<TuUsuario>\Documents\TicketsCofat\client
npm install
```

### 2. Copiar Logo a Carpeta Pública

```powershell
copy C:\Users\<TuUsuario>\Documents\TicketsCofat\client\src\assets\image.png C:\Users\<TuUsuario>\Documents\TicketsCofat\client\public\image.png
```

### 3. Build para Producción

```powershell
npm run build
```

Verifica que se generó `dist/`:

```powershell
dir dist
```

---

## Configuración de IIS

### 1. Crear Sitio Web

Abre IIS Manager (busca "IIS" en el menú Inicio).

- Crea un nuevo sitio: "TicketsCofat"
- Ruta física: `C:\Users\<TuUsuario>\Documents\TicketsCofat\client\dist`
- Puerto: 80

### 2. Configurar Proxy para API

Instala Application Request Routing (ARR) si no está instalado:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName IIS-ApplicationRequestRouting
```

En IIS Manager:

- Selecciona el sitio TicketsCofat
- Abre "URL Rewrite"
- Añade regla para `/api/*` que redirija a `http://localhost:8000/api/`
- Añade regla para `/admin/*` que redirija a `http://localhost:8000/admin/`

### 3. Configurar Permisos

Asegúrate que IIS_IUSRS tenga permisos de lectura en la carpeta del sitio.

---

## Configuración de Firewall

### Abrir Puertos en Firewall de Windows

```powershell
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

---

## Servicios con Windows Services

### 1. Crear Servicio para Django

Usa NSSM (Non-Sucking Service Manager) para crear un servicio.

Descarga NSSM: https://nssm.cc/download

```powershell
nssm install TicketsCofat "C:\Users\<TuUsuario>\Documents\TicketsCofat\venv\Scripts\python.exe" "C:\Users\<TuUsuario>\Documents\TicketsCofat\manage.py" "runserver" "127.0.0.1:8000"
nssm set TicketsCofat AppDirectory "C:\Users\<TuUsuario>\Documents\TicketsCofat"
nssm set TicketsCofat AppEnvironmentExtra DJANGO_SETTINGS_MODULE=tickets.settings
nssm start TicketsCofat
```

Para producción, mejor usa Waitress:

```powershell
nssm install TicketsCofat "C:\Users\<TuUsuario>\Documents\TicketsCofat\venv\Scripts\waitress-serve.exe" "--listen=127.0.0.1:8000" "tickets.wsgi:application"
nssm set TicketsCofat AppDirectory "C:\Users\<TuUsuario>\Documents\TicketsCofat"
nssm set TicketsCofat AppEnvironmentExtra DJANGO_SETTINGS_MODULE=tickets.settings
nssm start TicketsCofat
```

---

## Verificación y Debugging

### Verificar Servicios

```powershell
# Ver estado del servicio
Get-Service TicketsCofat

# Ver logs (depende de cómo configures logging)
```

### Pruebas de Conectividad

```powershell
# Desde el navegador
Start-Process "http://localhost"
Start-Process "http://localhost/api/"
```

### Si hay Errores de Permisos

Asegúrate que el usuario del servicio tenga permisos en la carpeta.

---

## HTTPS con Certificado (Opcional)

Para HTTPS, puedes usar Let's Encrypt con win-acme o configurar un certificado manualmente en IIS.

Descarga win-acme: https://github.com/win-acme/win-acme/releases

Ejecuta y sigue las instrucciones para obtener un certificado gratuito.

---

## Despliegues Futuros

### Actualizar Backend

```powershell
cd C:\Users\<TuUsuario>\Documents\TicketsCofat
git pull
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
Restart-Service TicketsCofat
```

### Actualizar Frontend

```powershell
cd C:\Users\<TuUsuario>\Documents\TicketsCofat\client
git pull
npm ci
npm run build
# Reinicia IIS
iisreset
```

### Ver Logs

```powershell
# Logs de IIS
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" -Tail 10

# Logs de Django (configura logging en settings.py)
```

---

## Troubleshooting

### Admin no carga (DisallowedHost)

Añade la IP local a `tickets/settings.py`:

```python
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,<TU_IP_LOCAL>').split(',')
```

O en el `.env`:

```
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,<TU_IP_LOCAL>
```

Luego reinicia el servicio.

### Logo no aparece en Frontend

El logo se sirve desde `/image.png` en la carpeta `client/public/`.

### Problemas de Conexión

Verifica que los puertos estén abiertos en el firewall y que IIS esté escuchando.

---