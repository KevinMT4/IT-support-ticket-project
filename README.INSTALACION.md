# Guía de Instalación de Herramientas - Windows 10

Esta guía explica paso a paso cómo instalar todas las herramientas necesarias para ejecutar el Sistema de Gestión de Tickets en Windows 10.

## Tabla de Contenidos

1. [Git](#1-git)
2. [Node.js](#2-nodejs)
3. [Python](#3-python)
4. [MySQL](#4-mysql)
5. [DBeaver](#5-dbeaver)
6. [Visual Studio Code](#6-visual-studio-code)
7. [Verificación Final](#7-verificación-final)

---

## 1. Git

Git es el sistema de control de versiones necesario para clonar el repositorio del proyecto.

### Descarga e Instalación

1. Abre tu navegador y visita: `https://git-scm.com/download/win`
2. Descarga el instalador de **64-bit Git for Windows Setup**
3. Ejecuta el archivo `.exe` descargado
4. Durante la instalación, acepta las opciones predeterminadas en cada pantalla
5. En la pantalla **"Adjusting your PATH environment"**, selecciona **"Git from the command line and also from 3rd-party software"**
6. Continúa con los valores predeterminados hasta finalizar

### Verificación

Abre el **Símbolo del sistema** (`cmd`) y ejecuta:

```
git --version
```

Deberías ver algo como: `git version 2.x.x.windows.x`

---

## 2. Node.js

Node.js es necesario para instalar las dependencias y ejecutar el servidor de desarrollo del frontend (React).

### Descarga e Instalación

1. Abre tu navegador y visita: `https://nodejs.org/es/`
2. Descarga la versión **LTS** (Long Term Support), recomendada para la mayoría de usuarios
3. Ejecuta el instalador `.msi` descargado
4. Acepta los términos de licencia
5. En la pantalla de componentes, asegúrate de que **"Add to PATH"** esté marcado
6. Sigue los pasos hasta completar la instalación

> **Importante:** Durante la instalación, puede aparecer una pantalla preguntando si deseas instalar herramientas adicionales para módulos nativos. Puedes omitir esa opción para este proyecto.

### Verificación

Abre un **Símbolo del sistema nuevo** y ejecuta:

```
node --version
npm --version
```

Deberías ver versiones como: `v20.x.x` y `10.x.x`

---

## 3. Python

Python es necesario para ejecutar el backend del sistema (Django).

### Descarga e Instalación

1. Abre tu navegador y visita: `https://www.python.org/downloads/windows/`
2. Descarga la versión más reciente de **Python 3.x** (por ejemplo, Python 3.11 o 3.12)
3. Ejecuta el instalador `.exe` descargado
4. **MUY IMPORTANTE:** En la primera pantalla del instalador, marca la casilla **"Add Python to PATH"** antes de continuar

   ![Checkbox Add Python to PATH]

5. Haz clic en **"Install Now"**
6. Espera a que finalice la instalación
7. Al terminar, haz clic en **"Disable path length limit"** si aparece esa opción (recomendado)

### Verificación

Abre un **Símbolo del sistema nuevo** y ejecuta:

```
python --version
pip --version
```

Deberías ver versiones como: `Python 3.x.x` y `pip 24.x.x`

> **Nota:** En algunos sistemas puede ser necesario usar `python3` en lugar de `python`.

---

## 4. MySQL

MySQL es el motor de base de datos que utiliza el sistema para almacenar toda la información.

### Descarga e Instalación (MySQL Installer)

1. Abre tu navegador y visita: `https://dev.mysql.com/downloads/installer/`
2. Descarga el instalador **"MySQL Installer for Windows"** (el archivo más grande, ~450 MB)
3. Ejecuta el instalador `.msi`
4. Selecciona el tipo de instalación **"Custom"** para mayor control, o **"Developer Default"** para instalación rápida
5. Asegúrate de que los siguientes componentes estén seleccionados:
   - **MySQL Server** (el motor principal)
   - **MySQL Workbench** (opcional, pero útil)
6. Haz clic en **"Next"** y luego en **"Execute"** para descargar e instalar los componentes
7. Durante la configuración del servidor:
   - **Config Type:** Development Computer
   - **Puerto:** `3306` (predeterminado)
   - **Authentication Method:** Use Strong Password Encryption (recomendado)
   - **Root Password:** Elige una contraseña segura y **anótala**, la necesitarás más adelante
   - **Windows Service:** Dejar activado para que MySQL inicie automáticamente con Windows
8. Haz clic en **"Execute"** para aplicar la configuración
9. Finaliza la instalación

### Verificación

Abre un **Símbolo del sistema nuevo** y ejecuta:

```
mysql --version
```

Deberías ver algo como: `mysql  Ver 8.x.x Distrib 8.x.x, for Win64`

---

## 5. DBeaver

DBeaver es una herramienta visual para administrar y consultar bases de datos. Permite crear la base de datos, ver tablas y ejecutar consultas SQL de forma cómoda.

### Descarga e Instalación

1. Abre tu navegador y visita: `https://dbeaver.io/download/`
2. Descarga la versión **Community Edition** para Windows (el instalador `.exe`)
3. Ejecuta el instalador descargado
4. Acepta los términos de licencia
5. Selecciona las opciones predeterminadas y finaliza la instalación

### Conectar DBeaver a MySQL

1. Abre DBeaver
2. Haz clic en el ícono de **"Nueva Conexión"** (enchufe con un signo `+`) en la barra superior
3. Selecciona **MySQL** y haz clic en **"Next"**
4. Completa los campos de conexión:
   - **Server Host:** `localhost`
   - **Port:** `3306`
   - **Username:** `root`
   - **Password:** La contraseña que definiste durante la instalación de MySQL
5. Haz clic en **"Test Connection"** para verificar que funciona correctamente
   - Si es la primera vez, DBeaver te pedirá descargar el driver de MySQL, acepta
6. Haz clic en **"Finish"**

### Crear la Base de Datos

Una vez conectado, puedes crear la base de datos del proyecto:

1. En el panel izquierdo, haz clic derecho sobre la conexión de MySQL
2. Selecciona **"Create New Database"**
3. Escribe el nombre: `TicketsCofatBD`
4. En **"Character Set"** selecciona `utf8mb4`
5. En **"Collation"** selecciona `utf8mb4_unicode_ci`
6. Haz clic en **"OK"**

---

## 6. Visual Studio Code

Visual Studio Code (VSCode) es el editor de código recomendado para trabajar con el proyecto.

### Descarga e Instalación

1. Abre tu navegador y visita: `https://code.visualstudio.com/`
2. Descarga el instalador para **Windows** (botón azul principal)
3. Ejecuta el instalador `.exe`
4. Durante la instalación, se recomienda marcar las siguientes opciones:
   - **"Agregar accion 'Abrir con Code' al menu contextual de archivos"**
   - **"Agregar accion 'Abrir con Code' al menu contextual de directorios"**
   - **"Agregar a PATH"** (muy importante)
5. Finaliza la instalación

### Extensiones Recomendadas

Una vez instalado VSCode, instala las siguientes extensiones para mejorar la experiencia de desarrollo:

1. Abre VSCode
2. Ve al panel de extensiones con `Ctrl + Shift + X`
3. Busca e instala cada una:

| Extension | Descripción |
|---|---|
| **Python** (Microsoft) | Soporte para Python y Django |
| **ES7+ React/Redux/React-Native snippets** | Atajos para React |
| **Prettier - Code formatter** | Formateo automático de código |
| **GitLens** | Herramientas avanzadas de Git |
| **Django** | Soporte para plantillas Django |
| **Auto Rename Tag** | Renombrado automático de etiquetas HTML |

---

## 7. Verificación Final

Una vez instaladas todas las herramientas, abre un **Símbolo del sistema** y ejecuta los siguientes comandos para confirmar que todo está correctamente instalado:

```
git --version
node --version
npm --version
python --version
pip --version
mysql --version
```

Todos deben mostrar una versión sin errores. Si alguno muestra un error como `'comando' no se reconoce como comando interno`, intenta cerrar y volver a abrir el Símbolo del sistema, o reiniciar Windows para que los cambios en el PATH surtan efecto.

---

## Siguientes Pasos

Una vez que todas las herramientas estén instaladas, sigue la guía principal del proyecto en el archivo `README.md` para:

1. Clonar el repositorio con Git
2. Configurar el entorno virtual de Python
3. Instalar las dependencias del backend (`pip install -r requirements.txt`)
4. Configurar las variables de entorno (archivo `.env`)
5. Aplicar las migraciones de base de datos
6. Instalar las dependencias del frontend (`npm install` en la carpeta `client`)
7. Iniciar el servidor de desarrollo

---

## Solución de Problemas Comunes

### Python no se reconoce en el CMD

- Cierra y vuelve a abrir el Símbolo del sistema
- Si sigue sin funcionar, busca **"Variables de entorno"** en el menú de inicio de Windows
- Haz clic en **"Editar las variables de entorno del sistema"**
- En **"Variables de usuario"**, selecciona `Path` y haz clic en **"Editar"**
- Verifica que la ruta de Python (por ejemplo `C:\Users\TuUsuario\AppData\Local\Programs\Python\Python311\`) esté en la lista
- Si no está, haz clic en **"Nuevo"** y agrega la ruta manualmente

### MySQL no se reconoce en el CMD

- Busca **"Variables de entorno"** en el menú de inicio
- Agrega la ruta de MySQL al PATH, usualmente: `C:\Program Files\MySQL\MySQL Server 8.0\bin`

### Node.js no se reconoce en el CMD

- Reinstala Node.js y asegúrate de que la opción **"Add to PATH"** esté marcada durante la instalación
- Reinicia Windows e intenta de nuevo

### Error al conectar DBeaver con MySQL

- Verifica que el servicio de MySQL esté corriendo: busca **"Servicios"** en el menú de inicio, encuentra **"MySQL80"** y asegúrate de que su estado sea **"En ejecución"**
- Confirma que el puerto `3306` no esté bloqueado por el firewall de Windows

