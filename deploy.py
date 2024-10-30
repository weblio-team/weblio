import os
import sys
import subprocess
import platform
import random
import logging

# Configurar el logger
def setup_logger():
    logger = logging.getLogger('deploy_logger')
    logger.setLevel(logging.DEBUG)
    
    # Crear un manejador para escribir en un archivo de log
    file_handler = logging.FileHandler('log.txt')
    file_handler.setLevel(logging.DEBUG)
    
    # Crear un manejador para escribir en la consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Crear un formato común para ambos manejadores
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Agregar ambos manejadores al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_python_command():
    """Devuelve el comando de Python adecuado para el sistema operativo."""
    if platform.system() == "Windows":
        return "py"
    else:
        return "python3"

def run_command(command, cwd=None):
    """Ejecuta un comando en el shell y verifica su resultado."""
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        logger.info(f"Error: El comando '{command}' falló.")
        sys.exit(result.returncode)

def check_github_auth():
    """Verifica si el usuario está autenticado en GitHub CLI."""
    result = subprocess.run("gh auth status", shell=True, capture_output=True, text=True)
    if "not logged in" in result.stdout:
        logger.info("No estás autenticado en GitHub. Inicia sesión usando `gh auth login`.")
        run_command("gh auth login")

def create_and_activate_venv():
    """Crea y activa un entorno virtual llamado 'venv'."""
    python_cmd = get_python_command()
    
    # Crear el entorno virtual si no existe
    if not os.path.isdir("venv"):
        logger.info("Creando entorno virtual en la carpeta 'venv'...")
        run_command(f"{python_cmd} -m venv venv")

    # Activar el entorno virtual según el sistema operativo
    logger.info("Activando el entorno virtual...")
    if platform.system() == "Windows":
        activate_script = ".\\venv\\Scripts\\activate"
    else:
        activate_script = "source ./venv/bin/activate"
    
    run_command(activate_script)

def generate_random_app_name():
    """Genera un nombre aleatorio de dos palabras para la app en Heroku."""
    adjectives = ["cool", "smart", "bright", "quick", "brave", "silent", "proud"]
    nouns = ["falcon", "panda", "wolf", "tiger", "eagle", "lion", "otter"]
    return f"{random.choice(adjectives)}-{random.choice(nouns)}"

def deploy_to_heroku():
    """Automatiza el despliegue en Heroku."""
    logger.info("Iniciando sesión en Heroku...")
    run_command("heroku login")

    # Generar un nombre de aplicación aleatorio y crear la aplicación en Heroku
    app_name = generate_random_app_name()
    logger.info(f"Creando la aplicación en Heroku con el nombre '{app_name}'...")
    run_command(f"heroku create {app_name}")
    
    # Configurar para deshabilitar la recolección de archivos estáticos
    logger.info("Deshabilitando la recolección de archivos estáticos en Heroku...")
    run_command(f"heroku config:set DISABLE_COLLECTSTATIC=1")
    
    # Establecer Heroku como remoto en Git
    logger.info(f"Configurando el repositorio de Heroku con el nombre '{app_name}'...")
    run_command(f"heroku git:remote -a {app_name}")
    
    # Realizar el push a Heroku
    logger.info("Desplegando la aplicación en Heroku...")
    run_command("git push heroku prod:main")
    
    # Migrar y poblar la base de datos en Heroku
    logger.info("Ejecutando migraciones en la base de datos de Heroku...")
    logger.info("Skipping... Se utilizaran las migraciones existentes")
    #run_command(f"heroku run python manage.py migrate")
    
    logger.info("Poblando la base de datos en Heroku...")
    logger.info("Skipping... Se utilizaran los datos existentes")
    #run_command(f"heroku run python populate.py import")
    
    # Abrir la aplicación en el navegador
    logger.info("Abriendo la aplicación en Heroku...")
    run_command(f"heroku open")

# Inicializar el logger
logger = setup_logger()

def main():
    try:
        if len(sys.argv) < 2:
            logger.error("Uso: py deploy.py <tag>")
            sys.exit(1)
        
        tag = sys.argv[1]
        repo_url = "https://github.com/weblio-team/weblio"
        clone_dir = "weblio"

        # Paso 0: Verificar autenticación en GitHub
        check_github_auth()

        # Paso 1: Clonar el repositorio
        if not os.path.isdir(clone_dir):
            logger.info(f"Clonando el repositorio {repo_url} con la etiqueta '{tag}' en '{clone_dir}'...")
            run_command(f"git clone --branch {tag} {repo_url} {clone_dir}")
        else:
            logger.info(f"El repositorio ya existe en '{clone_dir}'. Omitiendo clonación.")
        
        # Cambiar al directorio del repositorio clonado
        os.chdir(clone_dir)
        run_command("git checkout prod")

        # Paso 2: Crear y activar el entorno virtual
        create_and_activate_venv()

        # Usar el comando adecuado para Python
        python_cmd = get_python_command()
        
        # Paso 3: Instalar las dependencias
        logger.info("Instalando dependencias desde requirements.txt...")
        run_command(f"{python_cmd} -m pip install -r requirements.txt")
        
        # Paso 4: Ejecutar las migraciones de Django
        logger.info("Ejecutando migraciones en la base de datos Local...")
        run_command(f"{python_cmd} manage.py migrate")
        
        # Paso 5: Ejecutar el script populate.py con el argumento 'import'
        logger.info("Poblando la base de datos Local...")
        run_command(f"{python_cmd} populate.py import")
        
        # Paso 6: Desplegar en Heroku
        deploy_to_heroku()

        # Paso 7: Ejecutar el servidor de desarrollo de Django
        logger.info("Iniciando el servidor de Django localmente...")
        run_command(f"{python_cmd} manage.py runserver")
    finally:
        logging.shutdown()

if __name__ == "__main__":
    main()
