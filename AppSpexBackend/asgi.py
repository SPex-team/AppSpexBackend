"""
ASGI config for AppSpexBackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from . settings import project_env

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AppSpexBackend.settings')
settings = project_env.get_django_settings()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)

application = get_asgi_application()
