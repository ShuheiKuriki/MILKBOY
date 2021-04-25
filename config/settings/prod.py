from .common import *

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '.herokuapp.com']

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": 'INFO',
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "var/log/taskManager/django.log",
            "formatter": "production",
        },
    },
    "formatters": {
        "production": {
            "format": "\t".join(
                [
                    "[%(levelname)s]",
                    "%(asctime)s",
                    "%(process)d",
                    "%(thread)d",
                    "%(pathname)s",
                    "%(lineno)d",
                    "%(message)s",
                ]
            )
        },
    },
    "loggers": {
        "": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

import dj_database_url
DATABASES = {
    'default': dj_database_url.config()
}

SECRET_KEY = os.environ['SECRET_KEY']

import django_heroku

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.9/howto/static-files/

django_heroku.settings(locals(), staticfiles=False)
