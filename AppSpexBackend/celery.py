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
    'sync_new_miners': {
        'task': 'spex.tasks.sync_new_miners',
        'schedule': 60 * 2
    },
    'update_all_miners': {
        'task': 'spex.tasks.update_all_miners',
        'schedule': 60 * 5
    },
    'sync_new_orders': {
        'task': 'spex.tasks.sync_new_orders',
        'schedule': 60 * 5
    },
    'sync_loan_new_miners': {
        'task': 'loan.tasks.sync_new_miners',
        'schedule': 60 * 2
    },
    'update_loan_all_miners': {
        'task': 'loan.tasks.update_all_miners',
        'schedule': 60 * 5
    },
    'sync_loan_new_loans': {
        'task': 'loan.tasks.sync_new_loans',
        'schedule': 60 * 2
    },
    'update_loan_all_loans': {
        'task': 'loan.tasks.update_all_loans',
        'schedule': 60 * 5
    },
    'sync_new_withdraw_repayment': {
        'task': 'loan.tasks.sync_new_withdraw_repayment',
        'schedule': 60 * 5
    },
    'sync_new_wallet_repayment': {
        'task': 'loan.tasks.sync_new_wallet_repayment',
        'schedule': 60 * 5
    }
}
