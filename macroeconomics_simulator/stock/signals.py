import json
import os
import time

from django.db.models.signals import post_save
from django.dispatch import receiver

from macroeconomics_simulator import settings
from stock.models import GoldSilverExchange


@receiver(post_save, sender=GoldSilverExchange)
def fill_json_template_for_gold_silver_rate(sender, instance, created, **kwargs):
    json_path = os.path.join(settings.MEDIA_ROOT, 'gold_silver_rate', f"{instance.id}.json")
    if created:  # calculate current price and add in history
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        json_schema = {
            "base price": instance.base_price,
            "amount": instance.amount,
            "contents": []
        }

        with open(json_path, 'w') as file:
            json.dump(json_schema, file, indent=2)

        instance.history = json_path
        instance.save()
    else:
        with open(json_path, 'r') as file:
            json_data = json.load(file)

        json_data["contents"].append({
            "timestamp": int(time.time()),
            "current price": instance.current_price
        })

        with open(json_path, 'w') as file:
            json.dump(json_data, file, indent=2)
