import os
import django_heroku
import dj_database_url

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

DATABASES = {
    'default': dj_database_url.config()
}

SECRET_KEY = os.environ['SECRET_KEY']

TW_CONSUMER_KEY = os.environ['TW_CONSUMER_KEY']
TW_CONSUMER_SECRET = os.environ['TW_CONSUMER_SECRET']
TW_TOKEN = os.environ['TW_TOKEN']
TW_TOKEN_SECRET = os.environ['TW_TOKEN_SECRET']


django_heroku.settings(locals(), staticfiles=False)

CORS_REPLACE_HTTPS_REFERER = True
HOST_SCHEME = "https://"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 1000000
SECURE_FRAME_DENY = True
