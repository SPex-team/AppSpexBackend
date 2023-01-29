from .settings import *

DEBUG = False


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ssv_alert_service',
        'USER': 'root',
        'PASSWORD': 'wonders,1',
        'HOST': '127.0.0.1',
        'PORT': '3308'
    }
}

CELERY_BROKER_URL = "amqp://alert:alert,1@localhost/alert",

PROM_RULE_FILE = "/opt/prometheus-2.38.0.linux-amd64/rules/ssv_rules.yml"
PROM_BASE_URL = "http://127.0.0.1:9090"
PROM_ADDR = "127.0.0.1"

BASE_URL = "https://alert.hellman.team"
