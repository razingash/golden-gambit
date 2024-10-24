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
        'options': {'expires': 600}
    },
    'pay-dividends-every-night': {
        'task': 'stock.tasks.dividends_payment',
        'schedule': crontab(hour='0', minute='0'),
        'options': {'expires': 3600}
    },
    'update-daily-company-prices-every-day': {
        'task': 'stock.tasks.update_daily_company_prices',
        'schedule': crontab(hour='2', minute='0'),
        'options': {'expires': 1800}
    }
}
