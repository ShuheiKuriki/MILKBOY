"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import threading
import time

import requests
import schedule
from django.core.wsgi import get_wsgi_application

from milkboy.tweet import regular_tweet, auto_reply

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

application = get_wsgi_application()


def schedule_action():
    schedules = ["09:00", "12:00", "15:00", "18:00", "21:00"]
    for tweet_time in schedules:
        schedule.every().day.at(tweet_time).do(regular_tweet)


def access():
    while True:
        schedule.run_pending()
        time.sleep(1200)
        req = requests.get("https://www.milkboy-core-ai.herokuapp.com")
        print('successfully accessed' if req.status_code == requests.codes.ok else 'access failed')


def always():
    while True:
        auto_reply()


t = threading.Thread(target=schedule_action)
t2 = threading.Thread(target=access)
t3 = threading.Thread(target=always)
t.start()
t2.start()
t3.start()
