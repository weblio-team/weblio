@echo off

python manage.py loaddata initial_data\groups.json
python manage.py loaddata initial_data\members.json
python manage.py loaddata initial_data\posts.json