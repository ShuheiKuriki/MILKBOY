"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import time
import threading
import requests

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

application = get_wsgi_application()


def always():
    while True:
        time.sleep(300)
        requests.get("https://www.milkboy-core-ai.tech/milkboy/tweet/")
        print('tweeted')


t = threading.Thread(target=always)
t.start()
