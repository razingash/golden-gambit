import json
import os
import random
import time
from decimal import Decimal

from celery import shared_task
from django.db import transaction

from macroeconomics_simulator import settings
from services.critical_services import calculate_company_price
from stock.models import GoldSilverExchange, Player, Company, PlayerCompanies

"""
in order to trigger periodic tasks or events for websockets, you need to import model and consumer
"""
from stock.consumers import TopUsersConsumer, TopCompaniesConsumer

@shared_task # redis
def document_gold_silver_rate():
    gold_silver_stock = GoldSilverExchange.objects.afirst()

    json_path = os.path.join(settings.MEDIA_ROOT, 'gold_silver_rate', f"{gold_silver_stock.id}.json")

    with open(json_path, 'r') as file:
        json_data = json.load(file)

    json_data["contents"].append({
        "timestamp": int(time.time()),
        "current price": float(round(gold_silver_stock.current_price, 2))
    })

    with open(json_path, 'w') as file:
        json.dump(json_data, file, indent=2)

@shared_task # rabbitMQ
def dividends_payment(): # try again later abulk_update
    """                         WARNING UNREADY!!!
    To update companies correctly, you need to project the optimized code of the
    recalculate_company_price function and save it to a file in this functio
    """
    shareholders = PlayerCompanies.objects.select_related('company', 'player').all()
    pay_dividendes = []
    companies_recalculation = []

    for shareholder in shareholders:
        if not shareholder.isHead:
            shareholder.player.silver += Decimal(shareholder.shares_amount * shareholder.company.share_price)
            companies_recalculation.append(shareholder.company)
            pay_dividendes.append(shareholder)

    Player.objects.bulk_update(pay_dividendes, ['silver'])
    Company.objects.bulk_save()
    with transaction.atomic():
        Company.objects.bulk_update(companies_recalculation, ['some_field'])

    #for company in companies_recalculation:
    #    company.save(document=True)

@shared_task # rabbitMQ
def update_daily_company_prices(): # try again later abulk_update
    companies = Company.objects.all()
    companies_to_update = []

    for company in companies:
        company.daily_company_price = company.company_price
        companies_to_update.append(company)

    with transaction.atomic():
        Company.objects.bulk_update(companies_to_update, ['daily_company_price'])


""" testing(using redis) | Remove all later"""
@shared_task
def rand_company_price():
    company_silver = random.randint(300_00, 300_000)
    company_id = random.randint(1, 11)
    company = Company.objects.get(id=company_id)
    company.silver_reserve = company_silver
    company.company_price = calculate_company_price(company)
    company.save() # no point in fixing the price

@shared_task
def rand_user_gold(): # test
    new_gold = random.randint(1, 11)
    player_id = random.randint(1, 11)
    player = Player.objects.get(id=player_id)
    if player.gold == new_gold:
        player.gold += 1
    else:
        player.gold = new_gold
    player.save()
