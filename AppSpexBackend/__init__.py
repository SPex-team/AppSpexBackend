import pymysql
from .celery import app as celery_app

pymysql.install_as_MySQLdb()
# from .prometheus import start_result

__all__ = ('celery_app', )