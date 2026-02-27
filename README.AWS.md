# Guía de Despliegue en AWS - TicketsCofat

## Tabla de Contenidos
1. [Prerequisites y Configuración EC2](#prerequisites-y-configuración-ec2)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Configuración del Backend](#configuración-del-backend)
4. [Configuración del Frontend](#configuración-del-frontend)
5. [Configuración de Nginx](#configuración-de-nginx)
6. [Configuración de Firewall](#configuración-de-firewall)
7. [Servicios con Systemd](#servicios-con-systemd)
8. [Verificación y Debugging](#verificación-y-debugging)
9. [HTTPS con Let's Encrypt (Opcional)](#https-con-lets-encrypt-opcional)
10. [Despliegues Futuros](#despliegues-futuros)

---

## Prerequisites y Configuración EC2

### Lanzar Instancia EC2
- **Sistema Operativo**: Ubuntu 22.04 LTS o 20.04 LTS
- **Tipo de Instancia**: t3.small (o t3.medium según carga)
- **Almacenamiento**: 20 GB gp3
- **Security Group**: Abrir puertos:
  - TCP 22 (SSH)
  - TCP 80 (HTTP)
  - TCP 443 (HTTPS)

### Conectarse a la Instancia
```bash
ssh -i /ruta/a/tu-key.pem ubuntu@<PUBLIC_IP>
```

---

## Instalación de Dependencias

### Actualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### Instalar Python y Herramientas Necesarias
```bash
sudo apt install -y \
  python3 python3-venv python3-pip \
  git build-essential nginx ufw \
  curl certbot python3-certbot-nginx
```

### Instalar Node.js (para Frontend)
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

---

## Configuración del Backend

### 1. Clonar o Descargar el Repositorio
```bash
cd /home/ubuntu
git clone <tu-repo-url> TicketsCofat
# O si ya está descargado:
cd TicketsCofat
sudo chown -R ubuntu:ubuntu /home/ubuntu/TicketsCofat
```

### 2. Crear Variables de Entorno (.env)
Crea `/home/ubuntu/TicketsCofat/.env` con:
```
DJANGO_SECRET_KEY=tu_secreto_largo_aqui_cambiar_en_produccion
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,<TU_IP_PUBLICA>
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@example.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=tu-email@example.com
```

### 3. Crear Entorno Virtual e Instalar Dependencias
```bash
cd /home/ubuntu/TicketsCofat
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 4. Ejecutar Migraciones de Base de Datos
```bash
export $(grep -v '^#' .env | xargs)
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Crear Superusuario (Opcional)
```bash
python manage.py createsuperuser
```

---

## Configuración del Frontend

### 1. Instalar Dependencias
```bash
cd /home/ubuntu/TicketsCofat/client
npm ci
```

### 2. Copiar Logo a Carpeta Pública
```bash
cp /home/ubuntu/TicketsCofat/client/src/assets/image.png /home/ubuntu/TicketsCofat/client/public/image.png
```

### 3. Build para Producción
```bash
npm run build
```

Verifica que se generó `dist/`:
```bash
ls -la dist/
```

---

## Configuración de Nginx

### 1. Crear Configuración de Sitio
Edita o crea `/etc/nginx/sites-available/tickets`:
```bash
sudo nano /etc/nginx/sites-available/tickets
```

Copia y pega (reemplaza `<TU_IP_O_DOMINIO>` con tu IP pública o dominio):
```nginx
server {
    listen 80;
    server_name <TU_IP_O_DOMINIO>;

    root /home/ubuntu/TicketsCofat/client/dist;
    index index.html;

    # Servir archivos estáticos (frontend)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxear API al backend Gunicorn
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin Django
    location /admin/ {
        proxy_pass http://127.0.0.1:8000/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    error_log /var/log/nginx/tickets_error.log;
    access_log /var/log/nginx/tickets_access.log;
}
```

### 2. Activar Sitio y Validar Configuración
```bash
sudo ln -s /etc/nginx/sites-available/tickets /etc/nginx/sites-enabled/
sudo nginx -t
```

### 3. Ajustar Permisos y Reiniciar Nginx
```bash
sudo chmod 755 /home/ubuntu
sudo chmod 755 /home/ubuntu/TicketsCofat
sudo chmod 755 /home/ubuntu/TicketsCofat/client
sudo chown -R www-data:www-data /home/ubuntu/TicketsCofat/client/dist
sudo systemctl restart nginx
```

---

## Configuración de Firewall

### Habilitar UFW y Permitir Puertos
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## Servicios con Systemd

### 1. Crear Unidad para Gunicorn
Edita `/etc/systemd/system/gunicorn.service`:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Copia y pega:
```ini
[Unit]
Description=gunicorn daemon for TicketsCofat
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/TicketsCofat
EnvironmentFile=/home/ubuntu/TicketsCofat/.env
ExecStart=/home/ubuntu/TicketsCofat/venv/bin/gunicorn --access-logfile - --workers 3 --bind 127.0.0.1:8000 tickets.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Activar y Iniciar Gunicorn
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

---

## Verificación y Debugging

### Verificar Servicios Activos
```bash
# Gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -f

# Nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/tickets_error.log
sudo tail -f /var/log/nginx/tickets_access.log
```

### Pruebas de Conectividad
```bash
# Desde dentro de la instancia
curl -I http://127.0.0.1/
curl -I http://127.0.0.1/api/

# Desde tu máquina (reemplaza <TU_IP>)
curl -I http://<TU_IP>/
curl -I http://<TU_IP>/api/
```

### Si hay Errores de Permisos
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/TicketsCofat/
sudo systemctl restart gunicorn
```

---

## HTTPS con Let's Encrypt (Opcional)

Si tienes un dominio apuntando a tu IP:
```bash
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

**Nota**: Let's Encrypt no emite certificados para IPs públicas directas.

---

## Despliegues Futuros

### Actualizar Backend
```bash
cd /home/ubuntu/TicketsCofat
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Actualizar Frontend
```bash
cd /home/ubuntu/TicketsCofat/client
git pull
npm ci
npm run build
sudo chown -R www-data:www-data /home/ubuntu/TicketsCofat/client/dist
sudo systemctl reload nginx
```

### Ver Logs en Tiempo Real
```bash
# Backend
sudo journalctl -u gunicorn -f

# Nginx
sudo tail -f /var/log/nginx/tickets_error.log | grep -E 'error|warn'
```

---

## Troubleshooting

### Admin no carga (DisallowedHost)
Añade la IP publica a `tickets/settings.py`:
```python
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,<TU_IP>').split(',')
```
O en el `.env`:
```
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,<TU_IP>
```
Luego reinicia Gunicorn:
```bash
sudo systemctl restart gunicorn
```

### Logo no aparece en Frontend
El logo se sirve desde `/image.png` (archivo público de Nginx) en la carpeta `client/public/`.

### Timeout al conectar HTTP
Verifica Security Group en AWS Console:
- EC2 → Instances → Security → Inbound rules
- Asegúrate que HTTP (80) está abierto desde `0.0.0.0/0`

---

