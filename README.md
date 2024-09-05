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

### 4. Crear la aplicación en Heroku

```bash
heroku config:set DISABLE_COLLECTSTATIC=1
```

### 5. Desplegar en Heroku

Sube tus cambios al repositorio de Heroku:

```bash
heroku git:remote -a nombre-de-tu-app
git push heroku tu_rama_de_produccion:main
```

### 6. Migrar la base de datos en Heroku

```bash
heroku run python manage.py migrate
```

### 7. Crear un superusuario para el panel de administración

```bash
heroku run python manage.py createsuperuser
```

### 8. Encender el servicio de Heroku

```bash
heroku open
```

Ahora podrás acceder a la aplicación en Heroku en la URL proporcionada.

## 🔄 Generación de Datos con `populate.py`

El proyecto incluye un script llamado `populate.py`, el cual está diseñado para la creación y exportación de datos en formato `.json`. Este script es útil para poblar rápidamente la base de datos con información de ejemplo o para exportar datos existentes para su uso en otros entornos.

### Uso de `populate.py`

El script acepta dos parámetros principales:

- `import`: Permite importar datos desde archivos `.json` a la base de datos.
- `export`: Exporta los datos de la base de datos a archivos `.json`.

Los archivos generados o utilizados por este script se almacenan en un directorio llamado `populate`, que debe existir en el mismo nivel del script o será creado automáticamente.

### Ejemplo de uso

1. Para exportar datos de la base de datos a archivos `.json`, ejecuta el siguiente comando:

   ```bash
   python populate.py export
   ```

   Esto generará archivos `.json` dentro de la carpeta `populate/` con los datos correspondientes.

2. Para importar datos desde archivos `.json` a la base de datos:

   ```bash
   python populate.py import
   ```

   Esto leerá los archivos `.json` de la carpeta `populate/` y cargará los datos en la base de datos.

### Nota
Asegúrate de tener las dependencias y la base de datos correctamente configuradas antes de ejecutar el script, ya que es necesario para la correcta creación o importación de los datos.

## 📝 Documentación con Sphinx

Este proyecto usa Sphinx para la generación automática de la documentación técnica. La documentación de Sphinx permite mantener una guía actualizada sobre el uso y desarrollo del proyecto.

### 1. Compilar la documentación

Para compilar la documentación en formato HTML, ejecuta los siguientes comandos:

```bash
cd docs
make html
```

Esto generará una versión HTML de la documentación en la carpeta `_build/html`. Podrás abrir el archivo `index.html` en tu navegador para revisar la documentación.

### 2. Actualización de la documentación

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
