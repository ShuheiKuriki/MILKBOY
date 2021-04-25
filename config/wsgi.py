"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import time
import schedule
import threading
import requests

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

application = get_wsgi_application()

def always():
    while True:
        time.sleep(1000)
        requests.get("https://milkboy-core-ai.herokuapp.com/")
        print('wake up!')

t = threading.Thread(target=always)
t.start()
