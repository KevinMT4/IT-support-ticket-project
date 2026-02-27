# Sistema de Gestión de Tickets

Sistema web para la gestión de tickets de soporte técnico, desarrollado con Django (backend) y React (frontend).

## Descripción.

Este sistema permite a los usuarios crear y gestionar tickets de soporte dirigidos al departamento de Tecnologías de la Información. Los administradores pueden visualizar todos los tickets, cambiar su estado y prioridad, así como generar reportes en PDF.

### Características Principales

- **Autenticación y autorización**: Sistema de login y registro de usuarios
- **Gestión de tickets**: Creación, visualización y seguimiento de tickets
- **Roles de usuario**:
    - **Usuario**: Puede crear y ver sus propios tickets
    - **Administrador**: Puede ver todos los tickets, cambiar estados y prioridades
- **Departamentos y motivos**: Organización de tickets por departamentos y categorías
- **Reportes PDF**: Generación de reportes estadísticos semanales (solo administradores)
- **Notificaciones en tiempo real**: Alertas visuales y sonoras cuando cambia el estado de un ticket
- **Panel de estadísticas**: Visualización de métricas por estado, prioridad y departamento

## Tecnologías Utilizadas

### Backend

- Python 3.x
- Django 4.2.11
- Django REST Framework 3.14.0
- ReportLab 4.0.7 (generación de PDFs)
- MySQL (base de datos)

### Frontend

- React 19.2.0
- React Router DOM 7.13.0
- Vite 7.2.4

## Requisitos Previos

- Python 3.8 o superior
- Node.js 16.x o superior
- npm o yarn

## Instalación Local

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd <nombre-del-proyecto>
```

### 2. Configurar el Backend

#### Crear y activar entorno virtual

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Instalar dependencias

```bash
pip install -r requirements.txt
```

#### Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
# Django Configuration
DJANGO_SECRET_KEY=tu-clave-secreta-muy-segura-aqui
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,localhost:8000,127.0.0.1:8000

# Database Configuration (SQLite por defecto)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion-de-16-caracteres (https://myaccount.google.com/apppasswords)
DEFAULT_FROM_EMAIL=tu-correo@gmail.com
```

**Notas importantes sobre las variables de entorno:**

- `DJANGO_SECRET_KEY`: Clave secreta para Django. En producción debe ser una cadena aleatoria y segura de al menos 50 caracteres.
- `DJANGO_DEBUG`: Debe ser `True` para desarrollo y `False` para producción.
- `DJANGO_ALLOWED_HOSTS`: Lista de hosts permitidos separados por comas.
- `DATABASE_URL`: URL de conexión a la base de datos. Por defecto usa SQLite.

#### Aplicar migraciones

```bash
python manage.py migrate
```

#### Crear datos iniciales

El sistema incluye migraciones que crean automáticamente:

- 8 departamentos predefinidos (Calidad, Finanzas, Compras, Ventas, Ingeniería, Logística, Recursos Humanos, TI)
- 4 motivos para el departamento de TI (Internet, Programas, Contraseñas, Equipo)

### Internationalization

Motivos (reasons) now support an English translation field (`nombre_en`).
When the frontend or API request is made with English as the current language
(either via the React i18n settings or `Accept-Language: en` header), the
system will display the English name if available.  New motivos can be edited
in the Django admin and the English name entered manually.  The database
contains a migration that seeds common reasons with reasonable English
equivalents.

#### Crear superusuario (administrador)

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear un usuario administrador. Este usuario tendrá acceso completo al sistema.

#### Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

El backend estará disponible en `http://localhost:8000`

### 3. Configurar el Frontend

Abrir una nueva terminal (manteniendo el backend ejecutándose):

```bash
cd client
```

#### Instalar dependencias

```bash
npm install
```

#### Configurar variables de entorno del frontend

Crear un archivo `.env` en la carpeta `client` con el siguiente contenido:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_PROXY_PATH=/api

# Development Server
VITE_DEV_SERVER_PORT=5173

#Timepo de inactividad
VITE_INACTIVITY_TIMEOUT_MINUTES=40
VITE_WARNING_TIME_MINUTES=2
```

**Notas sobre las variables de entorno del frontend:**

- `VITE_API_BASE_URL`: URL base del backend de Django.
- `VITE_API_PROXY_PATH`: Ruta del proxy para las peticiones API.
- `VITE_DEV_SERVER_PORT`: Puerto donde se ejecutará el servidor de desarrollo de Vite.
- `VITE_INACTIVITY_TIMEOUT_MINUTES`: Tiempo de inactividad.
- `VITE_WARNING_TIME_MINUTES`: Ventana emergente que avisa en cuento tiempo cerrará sesión.

#### Iniciar el servidor de desarrollo

```bash
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## Uso del Sistema

### Para Usuarios Regulares

1. **Registro**:
    - Accede a `http://localhost:5173`
    - Haz clic en "Registrarse"
    - Completa el formulario con tu información
    - Selecciona tu departamento
    - Crea una contraseña segura (mínimo 8 caracteres)

2. **Crear un Ticket**:
    - Después de iniciar sesión, haz clic en "Nuevo Ticket"
    - Selecciona un motivo (opcional)
    - Escribe un asunto descriptivo
    - Describe detalladamente tu problema o solicitud
    - Haz clic en "Crear Ticket"

3. **Ver tus Tickets**:
    - En el panel principal verás todos tus tickets
    - Puedes filtrar por estado haciendo clic en las tarjetas de estadísticas
    - Haz clic en cualquier ticket para ver sus detalles completos

### Para Administradores

1. **Acceso al Sistema**:
    - Inicia sesión con las credenciales del superusuario creado
    - Verás una etiqueta "Admin" junto a tu nombre

2. **Gestión de Tickets**:
    - Visualiza todos los tickets del sistema
    - Accede a cualquier ticket para ver detalles
    - Cambia el estado: Abierto → En Proceso → Resuelto → Cerrado
    - Ajusta la prioridad: Baja, Media, Alta, Urgente

3. **Reportes PDF**:
    - Haz clic en "PDF Semanal" en el panel principal
    - Se generará un reporte con estadísticas de los últimos 7 días
    - Incluye gráficas de tickets por departamento, usuario, motivo y prioridad

4. **Panel de Administración Django**:
    - Accede a `http://localhost:8000/admin`
    - Gestiona usuarios, departamentos, motivos y tickets
    - Crea nuevos departamentos o motivos según sea necesario

## Estructura del Proyecto

```
project/
├── tickets/                    # Configuración principal de Django
│   ├── settings.py            # Configuración del proyecto
│   ├── urls.py                # URLs principales
│   └── wsgi.py                # WSGI config
├── ticket_system/             # Aplicación principal
│   ├── models.py              # Modelos de datos
│   ├── serializers.py         # Serializadores DRF
│   ├── api_views.py           # Vistas API REST
│   ├── api_urls.py            # URLs de la API
│   ├── admin.py               # Configuración del admin
│   └── migrations/            # Migraciones de base de datos
├── client/                    # Aplicación React
│   ├── src/
│   │   ├── api/               # Cliente API
│   │   ├── components/        # Componentes reutilizables
│   │   ├── context/           # Context API (Auth)
│   │   ├── hooks/             # Custom hooks
│   │   ├── pages/             # Páginas principales
│   │   ├── styles/            # Estilos CSS
│   │   └── utils/             # Utilidades
│   ├── package.json           # Dependencias npm
│   └── vite.config.js         # Configuración de Vite
├── manage.py                  # Script de gestión de Django
├── requirements.txt           # Dependencias Python
└── README.md                  # Este archivo
```

## Modelos de Datos

### Usuario (Usuario)

- Extiende el modelo User de Django
- Campos adicionales: `departamento`, `rol`
- Roles disponibles: user, admin, superuser

### Departamento

- `nombre`: Nombre del departamento
- `gerente`: Nombre del gerente
- `email`: Email del departamento
- `descripcion`: Descripción opcional
- `activo`: Estado del departamento

### Motivo

- `nombre`: Nombre del motivo
- `descripcion`: Descripción del motivo
- `departamento`: Departamento al que pertenece

### Ticket

- `usuario`: Usuario que creó el ticket
- `departamento`: Departamento de TI (siempre)
- `motivo`: Motivo del ticket (opcional)
- `asunto`: Asunto del ticket
- `contenido`: Descripción detallada
- `prioridad`: baja, media, alta, urgente
- `estado`: abierto, en_proceso, resuelto, cerrado
- `fecha_creacion`: Fecha y hora de creación
- `fecha_cierre`: Fecha y hora de cierre (si aplica)

## API Endpoints

### Autenticación

- `POST /api/login/` - Iniciar sesión
- `POST /api/logout/` - Cerrar sesión
- `POST /api/registro/` - Registrar nuevo usuario

### Tickets

- `GET /api/tickets/` - Listar tickets
- `POST /api/tickets/` - Crear ticket
- `GET /api/tickets/{id}/` - Detalle de ticket
- `POST /api/tickets/{id}/update_estado/` - Actualizar estado
- `POST /api/tickets/{id}/update_prioridad/` - Actualizar prioridad

### Catálogos

- `GET /api/departamentos/` - Listar departamentos
- `GET /api/motivos/` - Listar motivos
- `GET /api/motivos/?departamento={id}` - Motivos por departamento

### Reportes

- `GET /api/reportes/pdf-estadisticas/` - Generar PDF de estadísticas. Acepta parámetro opcional `?lang=es|en` para traducir el contenido según el idioma.

## Características Adicionales

### Notificaciones en Tiempo Real

- El sistema actualiza automáticamente la lista de tickets cada 2 segundos
- Muestra notificaciones visuales cuando cambia el estado o prioridad
- Reproduce sonidos para alertar cambios importantes

### Diseño Responsivo

- Interfaz adaptable a diferentes tamaños de pantalla
- Optimizado para desktop, tablet y móvil

### Seguridad

- Autenticación basada en tokens
- Row Level Security para acceso a datos
- Validación de permisos en backend y frontend
- CORS configurado para desarrollo local

## Solución de Problemas

### Error: No se puede conectar al backend

- Verifica que el servidor Django esté ejecutándose en `http://localhost:8000`
- Revisa las variables de entorno del frontend
- Comprueba que no haya conflictos de puertos

### Error: Migraciones pendientes

```bash
python manage.py migrate
```

### Error: Módulo no encontrado

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd client
npm install
```

### Error: Puerto en uso

```bash
# Cambiar puerto del backend (en manage.py o comando)
python manage.py runserver 8001

# Cambiar puerto del frontend (en .env)
VITE_DEV_SERVER_PORT=5174
```

### Error: Gmail no acepta las credenciales (535 5.7.8)

Este error ocurre cuando Gmail rechaza las credenciales de correo. Para solucionarlo:

**Paso 1: Activa la verificación en dos pasos en tu cuenta de Google**

1. Ve a https://myaccount.google.com/security
2. En "Iniciar sesión en Google", selecciona "Verificación en dos pasos"
3. Sigue las instrucciones para activarla

**Paso 2: Genera una contraseña de aplicación**

1. Ve a https://myaccount.google.com/apppasswords
2. Selecciona "Correo" como la aplicación
3. Selecciona "Otro (nombre personalizado)" como el dispositivo
4. Escribe "Sistema de Tickets" o el nombre que prefieras
5. Haz clic en "Generar"
6. Google te mostrará una contraseña de 16 caracteres (sin espacios)

**IMPORTANTE**:

- La contraseña de aplicación NO es tu contraseña normal de Gmail
- Son 16 caracteres generados por Google
- NO debe tener espacios
- Mantén esta contraseña segura

**Paso 4: Reinicia el servidor Django**

```bash
# Detén el servidor (Ctrl+C) y vuelve a iniciarlo
python manage.py runserver
```

**Para probar que funciona**:

- Crea un nuevo ticket como usuario regular
- El sistema debe enviarte un correo de confirmación
- Verifica tu bandeja de entrada y spam

## Comandos Útiles

### Backend

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar shell de Django
python manage.py shell

# Recolectar archivos estáticos
python manage.py collectstatic
```

### Frontend

```bash
# Desarrollo
npm run dev

# Build para producción
npm run build

# Preview de build
npm run preview

# Linter
npm run lint
```

## Notas de Producción

Para desplegar en producción, considera:

1. Cambiar `DJANGO_DEBUG=False` en el archivo `.env`
2. Usar una base de datos robusta (PostgreSQL, MySQL)
3. Configurar `DJANGO_ALLOWED_HOSTS` con el dominio real
4. Usar un servidor web como Nginx + Gunicorn
5. Configurar HTTPS/SSL
6. Implementar un sistema de respaldos
7. Configurar variables de entorno seguras
8. Usar un servicio de gestión de logs

## Licencia

[Especificar licencia]

## Contacto

[Información de contacto del equipo de desarrollo]
texto
