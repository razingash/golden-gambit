from celery import Celery
import os
from datetime import timedelta

from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macroeconomics_simulator.settings.dev')

app = Celery('macroeconomics_simulator')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'test-change-company-price-every-4-second': {  # delete later
        'task': 'stock.tasks.rand_company_price',
        'schedule': timedelta(seconds=4),
    },
    'test-change-gold-every-5-second': {  # delete later
        'task': 'stock.tasks.rand_user_gold',
        'schedule': timedelta(seconds=5),
    },
    'document-gold-silver-rate-every-hour': { # every hour?
        'task': 'stock.tasks.document_gold_silver_rate',
        'schedule': crontab(hour='1'),
        'options': {'expires': 600}
    },
    'attempt-to-change-the-market-every-2-hours': { # starts an event or changes its stage with a certain probability,
        'task': 'stock.tasks.attempt_to_run_event',
        'schedule': crontab(minute='0', hour='*/2'),
        'options': {'expires': 3600}
    },
    'accrue-passive-income-every-evening': {
        'task': 'stock.tasks.accrue_company_passive_income',
        'schedule': crontab(hour='22', minute='0'),
        'options': {'expires': 3600}
    },
    'pay-dividends-every-night': {
        'task': 'stock.tasks.dividends_payment',
        'schedule': crontab(hour='0', minute='0'),
        'options': {'expires': 3600}
    },
    'update-daily-company-prices-every-night': {
        'task': 'stock.tasks.update_daily_company_prices',
        'schedule': crontab(hour='2', minute='0'),
        'options': {'expires': 1800}
    }
}
