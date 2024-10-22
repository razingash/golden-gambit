from celery import Celery
import os
from datetime import timedelta

from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macroeconomics_simulator.settings.dev')

app = Celery('macroeconomics_simulator')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'test-change-silver-every-30-seconds': { # delete later one random user
        'task': 'stock.tasks.check_layer', # rand_user_gold
        'schedule': timedelta(seconds=30)
    },
    'test-change-gold-every-minute': {  # delete later one random user
        'task': 'stock.tasks.rand_user_gold',
        'schedule': crontab(minute='1'),
    },
    'test-change-gold-every-2-minutes': {  # delete later all users
        'task': 'stock.tasks.rand_users_gold',
        'schedule': crontab(minute='2'),
    },
    'test-change-gold-every-3-minutes': {  # delete later all users, but changings with sleeping
        'task': 'stock.tasks.rand_users_gold_2',
        'schedule': crontab(minute='3'),
    },
    'document-gold-silver-rate-every-hour': {
        'task': 'stock.tasks.document_gold_silver_rate',
        'schedule': crontab(hour='1'),
        'options': {'expires': 180}
    },
}
