import os
import sys
import subprocess
import platform
import random

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
        print(f"Error: El comando '{command}' falló.")
        sys.exit(result.returncode)

def check_github_auth():
    """Verifica si el usuario está autenticado en GitHub CLI."""
    result = subprocess.run("gh auth status", shell=True, capture_output=True, text=True)
    if "not logged in" in result.stdout:
        print("No estás autenticado en GitHub. Inicia sesión usando `gh auth login`.")
        run_command("gh auth login")

def create_and_activate_venv():
    """Crea y activa un entorno virtual llamado 'venv'."""
    python_cmd = get_python_command()
    
    # Crear el entorno virtual si no existe
    if not os.path.isdir("venv"):
        print("Creando entorno virtual en la carpeta 'venv'...")
        run_command(f"{python_cmd} -m venv venv")

    # Activar el entorno virtual según el sistema operativo
    print("Activando el entorno virtual...")
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
    print("Iniciando sesión en Heroku...")
    run_command("heroku login")

    # Generar un nombre de aplicación aleatorio y crear la aplicación en Heroku
    app_name = generate_random_app_name()
    print(f"Creando la aplicación en Heroku con el nombre '{app_name}'...")
    run_command(f"heroku create {app_name}")
    
    # Configurar para deshabilitar la recolección de archivos estáticos
    print("Deshabilitando la recolección de archivos estáticos en Heroku...")
    run_command(f"heroku config:set DISABLE_COLLECTSTATIC=1")
    
    # Establecer Heroku como remoto en Git
    print(f"Configurando el repositorio de Heroku con el nombre '{app_name}'...")
    run_command(f"heroku git:remote -a {app_name}")
    
    # Realizar el push a Heroku
    print("Desplegando la aplicación en Heroku...")
    run_command("git push heroku kevin:main")
    
    # Migrar y poblar la base de datos en Heroku
    print("Ejecutando migraciones en la base de datos de Heroku...")
    print("Skipping... Se utilizaran las migraciones por defecto")
    #run_command(f"heroku run python manage.py migrate")
    
    print("Poblando la base de datos en Heroku...")
    print("Skipping... Se utilizaran los datos por defecto")
    #run_command(f"heroku run python populate.py import")
    
    # Abrir la aplicación en el navegador
    print("Abriendo la aplicación en Heroku...")
    run_command(f"heroku open")

def main():
    if len(sys.argv) < 2:
        print("Uso: py deploy.py <tag>")
        sys.exit(1)
    
    tag = sys.argv[1]
    repo_url = "https://github.com/weblio-team/weblio"
    clone_dir = "weblio"

    # Paso 0: Verificar autenticación en GitHub
    check_github_auth()

    # Paso 1: Clonar el repositorio
    if not os.path.isdir(clone_dir):
        print(f"Clonando el repositorio {repo_url} con la etiqueta '{tag}' en '{clone_dir}'...")
        run_command(f"git config advice.detachedHead false")
        run_command(f"git clone --branch {tag} {repo_url} {clone_dir}")
    else:
        print(f"El repositorio ya existe en '{clone_dir}'. Omitiendo clonación.")
    
    # Cambiar al directorio del repositorio clonado
    os.chdir(clone_dir)
    run_command("git checkout kevin")

    # Paso 2: Crear y activar el entorno virtual
    create_and_activate_venv()

    # Usar el comando adecuado para Python
    python_cmd = get_python_command()
    
    # Paso 3: Instalar las dependencias
    print("Instalando dependencias desde requirements.txt...")
    run_command(f"{python_cmd} -m pip install -r requirements.txt")
    
    # Paso 4: Ejecutar las migraciones de Django
    print("Ejecutando migraciones de Django...")
    run_command(f"{python_cmd} manage.py migrate")
    
    # Paso 5: Ejecutar el script populate.py con el argumento 'import'
    print("Ejecutando populate.py con el argumento 'import'...")
    run_command(f"{python_cmd} populate.py import")
    
    # Paso 6: Desplegar en Heroku
    deploy_to_heroku()

    # Paso 7: Ejecutar el servidor de desarrollo de Django
    print("Iniciando el servidor de Django localmente...")
    run_command(f"{python_cmd} manage.py runserver")

if __name__ == "__main__":
    main()
