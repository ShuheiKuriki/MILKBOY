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
from twitter import Twitter, OAuth

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

application = get_wsgi_application()

def always():
    while True:
        time.sleep(300)
        api = Twitter(
            auth=OAuth(
                os.environ["TW_TOKEN"],
                os.environ["TW_TOKEN_SECRET"],
                os.environ["TW_CONSUMER_KEY"],
                os.environ["TW_CONSUMER_SECRET"]
            )
        )
        requests.get("https://www.milkboy-core-ai.tech/tweet")

t = threading.Thread(target=always)
t.start()
