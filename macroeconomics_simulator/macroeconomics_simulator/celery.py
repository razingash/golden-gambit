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
