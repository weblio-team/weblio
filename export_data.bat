@echo off
if not exist "initial_data" mkdir initial_data

python manage.py dumpdata auth.group --indent 4 > initial_data\groups.json
python manage.py dumpdata members --indent 4 > initial_data\members.json
python manage.py dumpdata posts --indent 4 > initial_data\posts.json

python check_encoding.py