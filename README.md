# Weblio - Blog CMS

![Python](https://img.shields.io/badge/Python-3.12.5-3776AB?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django)
![Heroku](https://img.shields.io/badge/Deployed_on-Heroku-430098?style=for-the-badge&logo=heroku)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Requests](https://img.shields.io/badge/Requests-2.32.3-0052CC?style=for-the-badge&logo=python)
![Pillow](https://img.shields.io/badge/Pillow-10.4.0-009688?style=for-the-badge&logo=python)
![Sphinx](https://img.shields.io/badge/Sphinx-8.0.2-000000?style=for-the-badge&logo=sphinx)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-7952B3?style=for-the-badge&logo=bootstrap)

Weblio es un proyecto de un CMS basado en Django para la creación de blogs. El proyecto está desplegado en Heroku y es compatible con Python 3.12.5.

## 🚀 Características principales

- CMS completo para la gestión de blogs.
- Interfaz rica en contenido, con un editor WYSIWYG gracias a `django-ckeditor`.
- Despliegue fácil en Heroku.
- Documentación automática mediante Sphinx.
- Estilizado con Bootstrap 5.3.0 para una interfaz moderna y responsiva.

## 🛠️ Tecnologías usadas

- **Lenguaje principal**: Python 3.12.5
- **Framework**: Django 5.1
- **Despliegue**: Heroku
- **Documentación**: Sphinx 8.0.2
- **CSS Framework**: Bootstrap 5.3.0

## 📦 Dependencias principales

Este proyecto utiliza las siguientes dependencias:

```bash
alabaster==1.0.0
asgiref==3.8.1
babel==2.16.0
bootstrap==5.3.0
certifi==2024.7.4
charset-normalizer==3.3.2
colorama==0.4.6
Django==5.1
django-ckeditor-5==0.2.13
docutils==0.21.2
idna==3.8
imagesize==1.4.1
Jinja2==3.1.4
MarkupSafe==2.1.5
packaging==24.1
piccolo_theme==0.24.0
pillow==10.4.0
Pygments==2.18.0
requests==2.32.3
snowballstemmer==2.2.0
Sphinx==8.0.2
sphinxcontrib-applehelp==2.0.0
sphinxcontrib-devhelp==2.0.0
sphinxcontrib-htmlhelp==2.1.0
sphinxcontrib-jsmath==1.0.1
sphinxcontrib-qthelp==2.0.0
sphinxcontrib-serializinghtml==2.0.0
sqlparse==0.5.1
tzdata==2024.1
urllib3==2.2.2
Unidecode==1.3.8
```

## 🔧 Instalación

Sigue los siguientes pasos para instalar el proyecto en tu entorno local.

### 1. Clonar el repositorio

```bash
git clone https://github.com/weblio-team/weblio.git
cd weblio
```

### 2. Crear un entorno virtual

Es recomendable crear un entorno virtual para aislar las dependencias del proyecto.

```bash
python3.12 -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

### 3. Instalar las dependencias

Instala todas las dependencias del proyecto con:

```bash
pip install -r requirements.txt
```

### 4. Configuración de variables de entorno

Asegúrate de configurar las siguientes variables de entorno necesarias para el despliegue en Heroku y la configuración de la base de datos.

```bash
SECRET_KEY=<tu-secret-key>
DEBUG=True
ALLOWED_HOSTS = ['.herokuapp.com', 'localhost', '127.0.0.1']
DATABASE_URL=<tu-url-de-base-de-datos>
```

### 5. Migraciones de base de datos

Aplica las migraciones a la base de datos:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Ejecutar el servidor local

Una vez configurado todo, puedes iniciar el servidor local con:

```bash
python manage.py runserver
```

## 🌐 Despliegue en Heroku

Para desplegar este proyecto en Heroku, sigue estos pasos:

### 1. Instalar Heroku CLI

Asegúrate de tener Heroku CLI instalada en tu sistema. Puedes seguir la documentación oficial [aquí](https://devcenter.heroku.com/articles/heroku-cli).

### 2. Inicia sesión en Heroku

```bash
heroku login
```

### 3. Crear la aplicación en Heroku

```bash
heroku create nombre-de-tu-app
```

### 4. Desplegar en Heroku

Sube tus cambios al repositorio de Heroku:

```bash
git push heroku tu_rama_de_produccion:main
```

### 5. Migrar la base de datos en Heroku

```bash
heroku run python manage.py migrate
```

### 6. Crear un superusuario para el panel de administración

```bash
heroku run python manage.py createsuperuser
```

### 7. Encender el servicio de Heroku

```bash
heroku open
```

Ahora podrás acceder a la aplicación en Heroku en la URL proporcionada.

## 🔨 Poblar la base de datos con datos de ejemplo

Puedes poblar la base de datos con datos de ejemplo usando los scripts `sample_data.bat` (para Windows) y `sample_data.sh` (para Mac/Linux). Estos scripts insertan datos predefinidos para que puedas probar el CMS rápidamente.

### En Windows

1. Abre una terminal de comandos (CMD) en la raíz del proyecto.
2. Ejecuta el siguiente comando:

```bash
sample_data.bat
```

### En Mac/Linux

1. Abre una terminal en la raíz del proyecto.
2. Da permisos de ejecución al script si es necesario:

```bash
chmod +x sample_data.sh
```

3. Ejecuta el script:

```bash
./sample_data.sh
```

### ¿Qué hacen estos scripts?

Estos scripts ejecutan una serie de comandos Django que crean y poblan la base de datos con contenido de ejemplo, como publicaciones, usuarios y comentarios.

## 📤 Exportación de datos

El script `export_data` te permite exportar los datos actuales de la base de datos a un archivo JSON. Esto es útil para hacer backups de los datos o moverlos entre diferentes entornos.

### Uso de `export_data` en Windows

1. Abre la terminal de comandos.
2. Ejecuta el siguiente comando:

```bash
export_data.bat
```

### Uso de `export_data` en Mac/Linux

1. Abre una terminal.
2. Da permisos de ejecución si es necesario:

```bash
chmod +x export_data.sh
```

3. Ejecuta el script:

```bash
./export_data.sh
```

Esto generará un archivo `.json` con los datos exportados, que luego podrás importar en otro entorno usando el comando `loaddata` de Django.

## 🛠️ Verificación de la codificación de archivos: `check_encoding`

El script `check_encoding` es una herramienta que verifica si los archivos del proyecto están usando la codificación correcta, lo cual es importante para evitar errores en diferentes sistemas operativos o con diferentes configuraciones locales.

### Uso en Windows

1. Abre la terminal de comandos.
2. Ejecuta el siguiente comando:

```bash
check_encoding.bat
```

### Uso en Mac/Linux

1. Abre una terminal.
2. Da permisos de ejecución al script:

```bash
chmod +x check_encoding.sh
```

3. Ejecuta el script:

```bash
./check_encoding.sh
```

Este script revisará todos los archivos en el proyecto y te notificará si encuentra archivos con codificación incorrecta.

## 📝 Documentación con Sphinx

Este proyecto usa Sphinx para la generación automática de la documentación técnica. La documentación de Sphinx permite mantener una guía actualizada sobre el uso y desarrollo del proyecto.

### 1. Instalación de Sphinx

Sphinx ya está incluido en las dependencias del proyecto. Para inicializar la documentación por primera vez, navega a la raíz del proyecto y ejecuta:

```bash
sphinx-quickstart docs
```

Esto generará una estructura básica de archivos dentro del directorio `docs`.

### 2. Compilar la documentación

Para compilar la documentación en formato HTML, ejecuta los siguientes comandos:

```bash
cd docs
make html
```

Esto generará una versión HTML de la documentación en la carpeta `_build/html`. Podrás abrir el archivo `index.html` en tu navegador para revisar la documentación.

### 3. Actualización de la documentación

Cada vez que hagas cambios en el código o desees actualizar la documentación, asegúrate de recompilarla con:

```bash
make html
```

## 📄 Licencia

**Integrantes del proyecto:**
- Kevin Galeano
- Majo Duarte
- Amanda Caceres
- Werner Uibrig

Este proyecto está bajo la licencia MIT. Puedes ver más detalles en el archivo `LICENSE`.
