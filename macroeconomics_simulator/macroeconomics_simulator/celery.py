from celery import Celery
import os

from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macroeconomics_simulator.settings')

app = Celery('macroeconomics_simulator')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'document-gold-silver-rate-every-hour': {
        'task': 'stock.tasks.document_gold_silver_rate',
        'schedule': crontab(hour='1'),
        'options': {'expires': 180}
    },
}
