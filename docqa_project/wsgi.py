"""
WSGI config for docqa_project project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docqa_project.settings')

application = get_wsgi_application()
