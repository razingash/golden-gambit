import json
import os
import time

from django.db.models.signals import post_save
from django.dispatch import receiver
from macroeconomics_simulator import settings
from stock.models import GoldSilverExchange, Company
from stock.services import calculate_share_price, calculate_company_price


@receiver(post_save, sender=Company)
def fill_json_template_for_company(sender, instance, created, **kwargs): # most likely will change in the future
    json_path = os.path.join(settings.MEDIA_ROOT, 'companies', f"{instance.ticker}.json")
    if created:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        json_schema = {
            "ticker": instance.ticker,
            "company_type": instance.company_type,
            "founding date": instance.founding_date,
            "contents": []
        }

        with open(json_path, 'w') as json_file:
            json.dump(json_schema, json_file, indent=2)

        instance.history = json_path
        # company_income is 0 because number of sold products = 0
        company_price = calculate_company_price(0, instance.company_type.cartoonist, instance.gold_reserve, instance.silver_reserve)
        instance.company_price = company_price
        instance.shares_price = calculate_share_price(company_price=company_price, shares_amount=instance.shares_amount)
        instance.save()
    else:
        with open(json_path, 'r') as json_file:
            json_data = json.load(json_file)

        json_data["contents"].append({
            "timestamp": int(time.time()),
            "company_price": instance.company_price,
            "silver_reserve": instance.silver_reserve,
            "gold_reserve": instance.gold_reserve
        })

        with open(json_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=2)


@receiver(post_save, sender=GoldSilverExchange)
def fill_json_template_for_company(sender, instance, created, **kwargs):
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

