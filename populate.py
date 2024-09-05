import os
import sys
import platform
import subprocess
from unidecode import unidecode
import re  # Para eliminar caracteres no alfabéticos


def find_and_replace_non_utf8_characters(content):
    """
    Función para reemplazar caracteres no UTF-8 y eliminar todo carácter que no sea alfabético.
    """
    fixed_content = bytearray()
    i = 0
    while i < len(content):
        try:
            # Intentar decodificar el byte siguiente como UTF-8
            content[i:i + 1].decode('utf-8')
            char = chr(content[i])

            # Reemplazar caracteres no alfabéticos por vacío
            if not re.match(r'[A-Za-z]', char):  # Mantener solo letras
                fixed_content.extend(b'')
            else:
                fixed_content.append(content[i])

            i += 1
        except UnicodeDecodeError:
            problematic_byte = content[i]
            print(f"Byte problemático en la posición {i}: {problematic_byte} (carácter: {chr(problematic_byte)})")
            # Reemplazar el byte problemático usando unidecode
            replacement = unidecode(chr(problematic_byte))
            fixed_content.extend(replacement.encode('utf-8'))
            i += 1

    return fixed_content


def read_json_file(file_path):
    """
    Leer archivo JSON como contenido binario.
    Validaciones:
        - Verificar que el archivo existe.
        - Asegurar que el archivo no esté vacío.
        - Detectar problemas de codificación UTF-8.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe.")

    if os.path.getsize(file_path) == 0:
        raise ValueError(f"El archivo {file_path} está vacío.")

    try:
        with open(file_path, 'rb') as file:
            content = file.read()
    except Exception as e:
        raise IOError(f"Error al leer el archivo {file_path}: {e}")

    try:
        # Verificar si el contenido es decodificable como UTF-8
        content.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError(f"El archivo {file_path} contiene caracteres no válidos en UTF-8.")

    return content


def process_files_for_encoding():
    """
    Procesar los archivos JSON en 'populate' para eliminar caracteres no UTF-8 y no alfabéticos.
    Validaciones:
        - Verificación de existencia de archivos.
        - Verificación de contenido no vacío.
        - Manejo de caracteres no válidos.
    """
    base_dir = os.path.join(os.path.dirname(__file__), 'populate')
    files = ['groups.json', 'members.json', 'posts.json']

    combined_content = bytearray()
    file_contents = {}

    for file_name in files:
        file_path = os.path.join(base_dir, file_name)

        try:
            # Leer y combinar contenido de todos los archivos
            content = read_json_file(file_path)
            file_contents[file_name] = content
            combined_content.extend(content)
        except (FileNotFoundError, ValueError, IOError) as e:
            print(f"Error procesando {file_name}: {e}")
            sys.exit(1)

    # Procesar el contenido combinado para limpiar caracteres
    try:
        fixed_combined_content = find_and_replace_non_utf8_characters(combined_content)
    except Exception as e:
        print(f"Error procesando caracteres en los archivos combinados: {e}")
        sys.exit(1)

    # Dividir y guardar el contenido limpio de nuevo en los archivos originales
    start = 0
    for file_name in files:
        original_content = file_contents[file_name]
        end = start + len(original_content)
        fixed_content = fixed_combined_content[start:end]
        start = end

        output_path = os.path.join(base_dir, file_name)
        try:
            with open(output_path, 'wb') as output_file:
                output_file.write(fixed_content)
            print(f"Procesado {file_name} y guardado contenido limpio en {output_path}")
        except IOError as e:
            print(f"Error al escribir en el archivo {output_path}: {e}")
            sys.exit(1)


def import_data():
    """
    Función para importar datos ejecutando los comandos adecuados
    según el sistema operativo (Windows o Linux/Mac).
    """
    if platform.system() == "Windows":
        # Comandos equivalentes a import_data.bat en Windows
        commands = [
            "python manage.py loaddata populate\\groups.json",
            "python manage.py loaddata populate\\members.json",
            "python manage.py loaddata populate\\posts.json"
        ]
    else:
        # Comandos equivalentes a import_data.sh en Linux/Mac
        commands = [
            "python manage.py loaddata populate/groups.json",
            "python manage.py loaddata populate/members.json",
            "python manage.py loaddata populate/posts.json"
        ]

    # Ejecutar los comandos
    run_commands(commands)


def export_data():
    """
    Función para exportar datos ejecutando los comandos adecuados
    según el sistema operativo (Windows o Linux/Mac).
    """
    if platform.system() == "Windows":
        # Comandos equivalentes a export_data.bat en Windows
        commands = [
            'if not exist "populate" mkdir populate',
            "python manage.py dumpdata auth.group --indent 4 > populate\\groups.json",
            "python manage.py dumpdata members --indent 4 > populate\\members.json",
            "python manage.py dumpdata posts --indent 4 > populate\\posts.json"
        ]
    else:
        # Comandos equivalentes a export_data.sh en Linux/Mac
        commands = [
            'mkdir -p populate',
            "python manage.py dumpdata auth.group --indent 4 > populate/groups.json",
            "python manage.py dumpdata members --indent 4 > populate/members.json",
            "python manage.py dumpdata posts --indent 4 > populate/posts.json"
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

    if action == "import":
        import_data()
    elif action == "export":
        export_data()
    else:
        print("Acción no reconocida. Usa 'import' o 'export'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
