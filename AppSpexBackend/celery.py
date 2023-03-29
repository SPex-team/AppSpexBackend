import os

from celery import Celery

from . import project_env

settings_name = project_env.get_django_settings()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_name)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
app = Celery(project_env.APP_NAME)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'create_alert': {
        'task': 'spex.tasks.sync_new_miners',
        'schedule': 60
    },
    'first_action': {
        'task': 'spex.tasks.update_all_miners',
        'schedule': 60 * 2
    }
}
