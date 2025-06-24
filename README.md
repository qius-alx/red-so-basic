# Sistema de Chat Avanzado - Universidad Nacional de Juliaca

## Carrera: Ingeniería de Software y Sistemas

---

## 📝 Descripción del Proyecto

Este proyecto es un sistema de chat avanzado desarrollado en Flask (Python) con extensiones como Flask-SocketIO, Flask-Bcrypt y Flask-MySQLdb. El objetivo inicial fue transformar un chat básico en una aplicación web completa con autenticación de usuarios, persistencia de datos en MySQL, y múltiples funcionalidades de comunicación e interacción, incluyendo un chat global, un foro de preguntas y respuestas, y (en desarrollo) chat privado entre usuarios y un panel de administración.

---

## ✨ Características Implementadas (Hasta Ahora)

*   **Sistema de Autenticación Completo:**
    *   Login de usuarios contra base de datos MySQL.
    *   Hashing seguro de contraseñas con bcrypt.
    *   Gestión de sesiones de usuario con Flask.
    *   Creación de usuario administrador mediante comando CLI (`flask create-admin`).
    *   Rutas protegidas que requieren inicio de sesión.
*   **Chat Global en Tiempo Real:**
    *   Comunicación instantánea entre todos los usuarios conectados.
    *   Persistencia de mensajes en base de datos MySQL.
    *   Límite automático de los últimos 30 mensajes visibles en el chat (gestionado por la base de datos).
    *   Carga del historial de mensajes al conectarse.
*   **Módulo de Preguntas y Respuestas (Foro):**
    *   Los usuarios pueden crear preguntas.
    *   Los usuarios pueden publicar respuestas a preguntas existentes.
    *   Visualización de preguntas con paginación.
    *   Vista detallada de cada pregunta con sus respuestas.
    *   Ordenamiento cronológico de preguntas y respuestas.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

*   **Python:** Versión 3.8 o superior.
*   **PIP:** Gestor de paquetes de Python (usualmente viene con Python).
*   **MySQL Server:** Versión 5.7 o superior (o un SGBD compatible como MariaDB).
*   **Git:** Para clonar el repositorio (opcional si descargas el código fuente directamente).

---

## ⚙️ Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu entorno local:

1.  **Clonar el Repositorio (Recomendado):**
    ```bash
    git clone <URL_DEL_REPOSITORIO_CUANDO_ESTE_DISPONIBLE>
    cd nombre-del-directorio-del-proyecto
    ```
    Si descargaste el código fuente como ZIP, descomprímelo y navega al directorio raíz.

2.  **Crear y Activar un Entorno Virtual:**
    Es altamente recomendable usar un entorno virtual para aislar las dependencias del proyecto.
    ```bash
    python -m venv venv
    ```
    Activación:
    *   En Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   En macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Instalar Dependencias:**
    Con el entorno virtual activado, instala las librerías de Python necesarias:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuración de la Base de Datos MySQL:**
    *   Asegúrate de que tu servidor MySQL esté en funcionamiento.
    *   Crea una base de datos para el proyecto. Por ejemplo, `chat_unaj`. Puedes usar un cliente MySQL como phpMyAdmin, DBeaver, o la línea de comandos:
        ```sql
        CREATE DATABASE chat_unaj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        ```
    *   Crea un usuario de MySQL con permisos para esta base de datos o usa un usuario existente (como `root` para desarrollo local, aunque no es recomendable para producción). Necesitarás el nombre de usuario, contraseña y host de la base de datos para el siguiente paso.

5.  **Configurar Variables de Entorno:**
    El proyecto utiliza un archivo `.env` para gestionar la configuración sensible.
    *   Crea un archivo llamado `.env` en el directorio raíz del proyecto.
    *   Copia el contenido del archivo `.env.example` (si existiera uno en el futuro, por ahora no se ha creado) o usa la siguiente plantilla y rellena los valores correspondientes a tu configuración de MySQL y una clave secreta para Flask:

        ```env
        # Flask App Configuration
        SECRET_KEY='tu_super_llave_secreta_aleatoria_y_dificil_de_adivinar'

        # MySQL Database Configuration
        MYSQL_HOST='localhost'         # O la IP/host de tu servidor MySQL
        MYSQL_USER='tu_usuario_mysql'  # Usuario de MySQL
        MYSQL_PASSWORD='tu_password_mysql' # Contraseña del usuario MySQL
        MYSQL_DB='chat_unaj'           # Nombre de la base de datos que creaste
        ```
        **Importante:** La `SECRET_KEY` debe ser una cadena larga, aleatoria y secreta. Puedes generar una con `python -c 'import secrets; print(secrets.token_hex(24))'`.

6.  **Estructura de Carpetas Principal:**
    Una visión general de la organización del proyecto:
    ```
    /tu-proyecto-raiz
    ├── app.py                # Archivo principal de la aplicación Flask
    ├── config.py             # Configuración de la aplicación
    ├── requirements.txt      # Dependencias de Python
    ├── schema.sql            # Definiciones de la estructura de la BD
    ├── .env                  # Variables de entorno (¡No subir a Git si es público!)
    ├── models/               # Modelos de datos (User, Message, Forum)
    ├── routes/               # Blueprints para organizar rutas (Auth, Chat, Forum)
    ├── static/               # Archivos estáticos (CSS, JS, imágenes)
    │   ├── css/
    │   └── js/
    ├── templates/            # Plantillas HTML (Jinja2)
    │   ├── auth/             # (login.html está en templates/ directamente por ahora)
    │   ├── chat.html
    │   ├── forum/
    │   └── base.html         # (Si se usa una plantilla base general)
    └── utils/                # Utilidades (conexión BD, decoradores, helpers)
    ```
---

## 🚀 Cómo Ejecutar el Proyecto

Una vez completada la instalación y configuración:

1.  **Crear las Tablas de la Base de Datos:**
    Ejecuta el script `schema.sql` para crear todas las tablas y triggers necesarios en la base de datos que configuraste (`chat_unaj` o el nombre que hayas elegido).
    Puedes hacerlo desde la línea de comandos de MySQL:
    ```bash
    mysql -u tu_usuario_mysql -p tu_base_de_datos < schema.sql
    ```
    (Reemplaza `tu_usuario_mysql` y `tu_base_de_datos` con tus credenciales y nombre de BD).
    O puedes importar `schema.sql` usando una herramienta gráfica de MySQL.

2.  **Crear el Usuario Administrador Inicial:**
    La aplicación incluye un comando CLI para crear el usuario administrador por defecto. Con tu entorno virtual activado, ejecuta:
    ```bash
    flask create-admin
    ```
    Esto creará el usuario `62528438` con la contraseña `2023107007` y rol `admin`.
    Puedes también especificar un usuario y contraseña diferentes:
    ```bash
    flask create-admin <tu_usuario_admin> <tu_contraseña_admin>
    ```

3.  **Ejecutar la Aplicación Flask:**
    Con el entorno virtual activado y desde el directorio raíz del proyecto:
    ```bash
    python app.py
    ```
    O, alternativamente (si tienes `FLASK_APP=app.py` configurado en tu entorno o `.flaskenv`):
    ```bash
    flask run
    ```
    Deberías ver un mensaje indicando que el servidor de desarrollo está corriendo, usualmente en `http://127.0.0.1:5000/`.

4.  **Acceder a la Aplicación:**
    Abre tu navegador web y ve a:
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

    Serás redirigido a la página de login.

---

## 👤 Credenciales por Defecto

*   **Usuario Administrador:**
    *   Usuario: `62528438`
    *   Contraseña: `2023107007`

**Nota:** Actualmente, la gestión de usuarios (cambiar contraseñas, agregar más usuarios no administradores) se realizará a través del Panel de Administración, que es una funcionalidad futura. Para cambiar la contraseña del admin, puedes volver a ejecutar `flask create-admin 62528438 nueva_contraseña`.

---

## 📱 Cómo Usar las Funcionalidades Implementadas

### 1. Inicio de Sesión (Login)
*   Accede a la URL raíz ([http://127.0.0.1:5000/](http://127.0.0.1:5000/)).
*   Serás redirigido a la página de login (`/auth/login`).
*   Ingresa tus credenciales (ej. las del administrador) y haz clic en "Ingresar".
*   Si las credenciales son correctas, serás redirigido a la página principal del chat global (`/chat/`).

### 2. Chat Global
*   Una vez logueado, accederás al chat global (`/chat/`).
*   Aquí puedes ver los mensajes de otros usuarios conectados y los mensajes históricos (hasta los últimos 30).
*   Escribe tu mensaje en el campo de texto inferior y presiona "Enviar" o Enter. Tu mensaje aparecerá y será visible para todos los demás usuarios en tiempo real.

### 3. Foro de Preguntas y Respuestas
*   **Acceder al Foro:** Navega a `/forum/` (puede que necesites añadir un enlace en la interfaz principal o escribir la URL directamente por ahora, ya que no hay una barra de navegación global implementada que enlace todas las secciones).
*   **Ver Preguntas:** En la página principal del foro, verás una lista de todas las preguntas realizadas, con su título, autor y fecha. Hay controles de paginación si hay muchas preguntas.
*   **Hacer una Nueva Pregunta:**
    *   Haz clic en el botón "Hacer una Nueva Pregunta" (o similar) en la página de listado de preguntas.
    *   Serás llevado a un formulario (`/forum/ask`).
    *   Ingresa un título y el contenido de tu pregunta.
    *   Haz clic en "Publicar Pregunta". Serás redirigido a la página de tu nueva pregunta.
*   **Ver una Pregunta y sus Respuestas:**
    *   Desde la lista de preguntas, haz clic en el título de cualquier pregunta.
    *   Esto te llevará a la página de la pregunta (`/forum/question/<id>`), donde verás el contenido completo de la pregunta y todas las respuestas publicadas para ella.
*   **Responder una Pregunta:**
    *   En la página de visualización de una pregunta, encontrarás un formulario para "Publicar una Respuesta".
    *   Escribe tu respuesta y haz clic en "Enviar Respuesta". Tu respuesta aparecerá debajo de la pregunta.

---

## 🔧 Configuración Técnica Adicional (Resumen)

*   **Flask:**
    *   `SECRET_KEY`: Configurada en `.env`. Esencial para la seguridad de las sesiones.
    *   `DEBUG` mode: Activado por defecto al ejecutar `python app.py` o `flask run` (ya que `debug=True` se pasa a `app.run` o `socketio.run`). Desactivar en producción.
*   **MySQL:**
    *   Los detalles de conexión (`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`) se gestionan en el archivo `.env`.
*   **Socket.IO:**
    *   Configurado para permitir todas las procedencias (`cors_allowed_origins="*"`). Para producción, esto debería restringirse a los dominios permitidos.

---

## 🐛 Solución de Problemas Comunes (Básico)

*   **Error `ModuleNotFoundError`:** Asegúrate de haber activado tu entorno virtual (`source venv/bin/activate` o `.\venv\Scripts\activate`) antes de ejecutar `pip install` o la aplicación.
*   **Errores de Conexión a Base de Datos (`(2002, "Can't connect to local MySQL server...")` o similar):**
    *   Verifica que tu servidor MySQL esté en funcionamiento.
    *   Confirma que las credenciales (`MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_DB`) en tu archivo `.env` sean correctas y coincidan con tu configuración de MySQL.
    *   Asegúrate de que el usuario de MySQL tenga permisos para acceder a la base de datos especificada desde el host especificado (usualmente `localhost` o `127.0.0.1`).
*   **Comando `flask` no encontrado:**
    *   Asegúrate de que el entorno virtual esté activado.
    *   Verifica que Flask esté instalado (`pip show flask`).
    *   Puede que necesites configurar la variable de entorno `FLASK_APP=app.py` (ej. `export FLASK_APP=app.py` en Linux/macOS o `set FLASK_APP=app.py` en Windows CMD).
*   **Problemas con Socket.IO (mensajes no llegan, etc.):**
    *   Revisa la consola del navegador (usualmente F12) y la consola del servidor Flask para mensajes de error.
    *   Asegúrate de que el cliente Socket.IO en `templates/chat.html` se esté conectando al namespace correcto (ej. `/chat`).
    *   Verifica que no haya bloqueos de firewall o problemas de red si accedes desde otra máquina.

---

Este README se actualizará a medida que se implementen más funcionalidades.
