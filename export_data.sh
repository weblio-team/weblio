#!/bin/bash

# Crear la carpeta initial_data si no existe
if [ ! -d "initial_data" ]; then
  mkdir initial_data
fi

# Exportar datos
python manage.py dumpdata auth.group --indent 4 > initial_data/groups.json
python manage.py dumpdata members --indent 4 > initial_data/members.json
python manage.py dumpdata posts --indent 4 > initial_data/posts.json

# Verificar y corregir la codificación
python check_encoding.py initial_data/groups.json
python check_encoding.py initial_data/members.json
python check_encoding.py initial_data/posts.json