import json
import os
import time

from celery import shared_task

from macroeconomics_simulator import settings
from stock.models import GoldSilverExchange


@shared_task # redis
def document_gold_silver_rate():
    gold_silver_stock = GoldSilverExchange.objects.first()

    json_path = os.path.join(settings.MEDIA_ROOT, 'gold_silver_rate', f"{gold_silver_stock.id}.json")

    with open(json_path, 'r') as file:
        json_data = json.load(file)

    json_data["contents"].append({
        "timestamp": int(time.time()),
        "current price": gold_silver_stock.current_price
    })

    with open(json_path, 'w') as file:
        json.dump(json_data, file, indent=2)

@shared_task # rabbitMQ
def dividends_payment():
    pass
