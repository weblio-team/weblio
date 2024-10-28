import os
import sys
import platform
import subprocess
import json
import re
import chardet

# Diccionario de reemplazo de caracteres acentuados y especiales
replacements = {
    'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a', 'ã': 'a', 'å': 'a', 'æ': 'ae',
    'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
    'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
    'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o', 'õ': 'o', 'ø': 'o',
    'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
    'ý': 'y', 'ÿ': 'y',
    'ñ': 'n', 'ç': 'c', 'ß': 'ss',

    'Á': 'A', 'À': 'A', 'Ä': 'A', 'Â': 'A', 'Ã': 'A', 'Å': 'A', 'Æ': 'AE',
    'É': 'E', 'È': 'E', 'Ë': 'E', 'Ê': 'E',
    'Í': 'I', 'Ì': 'I', 'Ï': 'I', 'Î': 'I',
    'Ó': 'O', 'Ò': 'O', 'Ö': 'O', 'Ô': 'O', 'Õ': 'O', 'Ø': 'O',
    'Ú': 'U', 'Ù': 'U', 'Ü': 'U', 'Û': 'U',
    'Ý': 'Y',
    'Ñ': 'N', 'Ç': 'C',

    'Œ': 'OE', 'œ': 'oe', 'Š': 'S', 'š': 's', 'Ž': 'Z', 'ž': 'z', 'Ð': 'D', 'ð': 'd',
    'Þ': 'TH', 'þ': 'th'
}

def find_populate_directory():
    """
    Busca la carpeta 'populate' en el directorio actual y retorna la ruta absoluta.
    
    :return: Ruta absoluta de la carpeta 'populate' o None si no se encuentra.
    """
    current_directory = os.getcwd()
    for root, dirs, _ in os.walk(current_directory):
        if 'populate' in dirs:
            return os.path.abspath(os.path.join(root, 'populate'))
    return None

# Función para reemplazar caracteres acentuados por su equivalente sin acento
def replace_accented_characters(text):
    if text is None:
        return ""
    for accented_char, replacement in replacements.items():
        text = text.replace(accented_char, replacement)
    return text

# Función para limpiar caracteres especiales de los campos
def clean_special_characters(text):
    text = replace_accented_characters(text)        # Reemplazar los caracteres acentuados primero
    return re.sub(r'[^A-Za-z0-9 ]+', '', text)      # Mantener solo letras, números y espacios

# Función para procesar el campo 'body', solo aplicando replacements sin eliminar otros caracteres
def process_body_field(text):
    return replace_accented_characters(text)  # Solo reemplazar caracteres del diccionario

def process_json_content(json_data):
    """
    Procesa el contenido JSON:
    - Para 'posts.category', reemplaza caracteres acentuados en 'name', 'description' y 'alias'.
    - Para 'posts.historicalpost' y 'posts.post', reemplaza caracteres acentuados en 'title', 'title_tag', 'keywords', y aplica solo replacements al 'body'.
    """
    if isinstance(json_data, list):
        for item in json_data:
            model = item.get('model')
            if 'fields' in item:
                fields = item['fields']
                # Procesar campos de 'posts.category'
                if model == 'posts.category':
                    if 'name' in fields:
                        fields['name'] = clean_special_characters(fields['name'])
                    if 'description' in fields:
                        fields['description'] = clean_special_characters(fields['description'])
                    if 'alias' in fields:
                        fields['alias'] = clean_special_characters(fields['alias'])
                # Procesar campos de 'posts.historicalpost' o 'posts.post'
                elif model in ['posts.historicalpost', 'posts.post']:
                    if 'title' in fields:
                        fields['title'] = clean_special_characters(fields['title'])
                    if 'title_tag' in fields:
                        fields['title_tag'] = clean_special_characters(fields['title_tag'])
                    if 'keywords' in fields:
                        fields['keywords'] = clean_special_characters(fields['keywords'])
                    if 'body' in fields:
                        # Solo reemplazar acentos en 'body' sin eliminar otros caracteres especiales
                        fields['body'] = process_body_field(fields['body'])
    return json_data

def read_and_process_json_file(file_path):
    """
    Leer un archivo JSON detectando su codificación automáticamente con chardet,
    procesarlo para reemplazar caracteres especiales, y devolver el contenido procesado.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe.")
    
    # Detectar la codificación automáticamente
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        #print(f"Codificación detectada: {encoding}")

    # Leer el archivo con la codificación detectada
    with open(file_path, 'r', encoding=encoding, errors='replace') as file:
        try:
            content = json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al decodificar JSON en {file_path}: {e}")
    
    # Procesar el contenido del JSON
    processed_content = process_json_content(content)
    
    return processed_content

def save_processed_json(file_path, content):
    """
    Guardar el contenido JSON procesado de nuevo en el archivo.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)
        print(f"Contenido procesado guardado en {file_path}")

def process_files_for_encoding():
    """
    Procesar los archivos JSON en 'populate' para eliminar caracteres acentuados y especiales.
    """
    base_dir = os.path.join(os.path.dirname(__file__), 'populate')
    files = ['groups.json', 'members.json', 'posts.json']

    for file_name in files:
        file_path = os.path.join(base_dir, file_name)

        try:
            # Leer, procesar y guardar contenido de cada archivo
            content = read_and_process_json_file(file_path)
            save_processed_json(file_path, content)
        except (FileNotFoundError, ValueError, IOError) as e:
            print(f"Error procesando {file_name}: {e}")
            sys.exit(1)

def import_data(populate_directory):
    """
    Función para importar datos ejecutando los comandos adecuados
    según el sistema operativo (Windows o Linux/Mac).
    """
    if platform.system() == "Windows":
        # Comandos equivalentes a import_data.bat en Windows
        commands = [
            f"python manage.py loaddata {populate_directory}\\groups.json",
            f"python manage.py loaddata {populate_directory}\\members.json",
            f"python manage.py loaddata {populate_directory}\\posts.json"
        ]
    else:
        # Comandos equivalentes a import_data.sh en Linux/Mac
        commands = [
            f"python3 manage.py loaddata {populate_directory}/groups.json",
            f"python3 manage.py loaddata {populate_directory}/members.json",
            f"python3 manage.py loaddata {populate_directory}/posts.json"
        ]

    # Ejecutar los comandos
    run_commands(commands)


def export_data(populate_directory):
    """
    Función para exportar datos ejecutando los comandos adecuados
    según el sistema operativo (Windows o Linux/Mac).
    """
    if platform.system() == "Windows":
        # Comandos equivalentes a export_data.bat en Windows
        commands = [
            f'if not exist "{populate_directory}" mkdir {populate_directory}',
            f"python manage.py dumpdata auth.group --indent 4 > {populate_directory}\\groups.json",
            f"python manage.py dumpdata members --indent 4 > {populate_directory}\\members.json",
            f"python manage.py dumpdata posts --indent 4 > {populate_directory}\\posts.json"
        ]
    else:
        # Comandos equivalentes a export_data.sh en Linux/Mac
        commands = [
            f'mkdir -p {populate_directory}',
            f"python3 manage.py dumpdata auth.group --indent 4 > {populate_directory}/groups.json",
            f"python3 manage.py dumpdata members --indent 4 > {populate_directory}/members.json",
            f"python3 manage.py dumpdata posts --indent 4 > {populate_directory}/posts.json"
        ]

    # Ejecutar los comandos
    run_commands(commands)

    # Después de exportar los datos, procesar los archivos para eliminar caracteres no válidos
    process_files_for_encoding()


def run_commands(commands):
    """
    Función para ejecutar una lista de comandos en el sistema.
    Captura excepciones si algún comando falla.
    """
    for command in commands:
        try:
            if platform.system() == "Windows":
                subprocess.run(command, check=True, shell=True)
            else:
                subprocess.run(command, check=True, shell=True, executable="/bin/bash")
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {command}. Error: {e}")
            sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Uso: python populate.py <import|export>")
        sys.exit(1)

    action = sys.argv[1].lower()
    
    populate_directory = find_populate_directory()
    if not populate_directory:
        print("La carpeta 'populate' no se encontró en el directorio actual")
        sys.exit(1)

    if action == "import":
        import_data(populate_directory)
    elif action == "export":
        export_data(populate_directory)
    else:
        print("Acción no reconocida. Usa 'import' o 'export'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
