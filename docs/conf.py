import os
import sys
import django

from datetime import date

sys.path.insert(0, os.path.abspath('..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'weblio.settings'
django.setup()

project = "Weblio"
copyright = f"{date.today().year}, Weblio Team"
author = "Weblio Team"
release = "1.0"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary', 
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode'
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "piccolo_theme"
html_static_path = ["_static"]