import json
import os
import random
import time
from decimal import Decimal

from celery import shared_task
from django.db import transaction
from django.db.models import Sum, F

from macroeconomics_simulator import settings
from services.critical_services import calculate_company_price
from stock.models import GoldSilverExchange, Player, Company, PlayerCompanies

"""
in order to trigger periodic tasks or events for websockets, you need to import model and consumer
"""
from stock.consumers import TopUsersConsumer, TopCompaniesConsumer

@shared_task # redis
def document_gold_silver_rate():
    gold_silver_stock = GoldSilverExchange.objects.first()

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
def accrue_company_passive_income():
    """passive income is available only to companies that manage gold,
     and it depends on the cartoonist and current events"""
    gold_silver_rate = GoldSilverExchange.objects.first()
    companies = Company.objects.select_related('type').filter(gold_reserve__gt=0)
    companies_to_update = []

    for company in companies:
        income = int((gold_silver_rate.current_price * company.gold_reserve) * (1 + company.type.cartoonist))
        company.silver_reserve += income
        companies_to_update.append(company)

    with transaction.atomic():
        Company.objects.bulk_update(companies_to_update, ['silver_reserve'])


@shared_task # rabbitMQ | this one need personal worker
def dividends_payment(): # try again later abulk_update
    """At the beginning, dividends are paid and then the company’s value is recalculated"""

    companies = Company.objects.prefetch_related('companywarehouse_set').all()
    shareholders = PlayerCompanies.objects.select_related('company', 'player').all()
    pay_dividendes = []
    companies_recalculation = []

    gold_rate_current_price = GoldSilverExchange.objects.only('current_price').first().current_price

    for shareholder in shareholders: # оставить как есть
        if not shareholder.isHead:
            shareholder.player.silver += Decimal(shareholder.shares_amount * shareholder.company.share_price)
            pay_dividendes.append(shareholder)

    for company in companies:
        company_silver = company.silver_reserve
        warehouses = company.companywarehouse_set.annotate(
            sale_price=F('product__productsexchange__sale_price')).aggregate(
            company_income=Sum(F('amount') * F('sale_price'))
        )
        company_income = warehouses['company_income'] if warehouses['company_income'] is not None else 0

        if company.gold_reserve > 0:
            gold_price = gold_rate_current_price * company.gold_reserve
            assets_price = gold_price + company_silver
        else:
            assets_price = company_silver

        shares_amount = Decimal(company.shares_amount)
        share_price = Decimal(company.share_price)
        dividendes_percent = Decimal(company.dividendes_percent)

        commitment = round(Decimal(shares_amount * share_price * dividendes_percent / 100), 2)

        company.company_price = (assets_price + company_income) - commitment
        companies_recalculation.append(company)

    with transaction.atomic():
        Player.objects.bulk_update(pay_dividendes, ['silver'])
        Company.objects.bulk_update(companies_recalculation, ['company_price'])


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
