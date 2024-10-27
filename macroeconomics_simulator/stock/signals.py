import json
import os

from django.db.models.signals import post_save
from django.dispatch import receiver

from macroeconomics_simulator import settings
from stock.models import GoldSilverExchange, CompanyWarehouse, Company, AvailableProductsForProduction

@receiver(post_save, sender=Company)
def create_company_warehouse(sender, instance, created, **kwargs):
    if created:
        product_instance = AvailableProductsForProduction.objects.get(company_type=instance.type).product_type
        CompanyWarehouse.objects.create(company=instance, product=product_instance, max_amount=50_000)


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
