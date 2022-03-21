"""
WSGI config for Chappbooking project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from Chappbooking.wsgi import ChappbookinApplication

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Chappbooking.settings')

application = ChappbookinApplication(application)
