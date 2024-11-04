import json
import os
import datetime
import random
from decimal import Decimal

from django.core.management import BaseCommand
from django.utils import timezone

from macroeconomics_simulator import settings
from services.events.E_services import events_manager
from stock.models import GoldSilverExchange, Player, Company, PlayerCompanies, SharesExchange


class Command(BaseCommand):
    help = "command to fill database with random data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('generating random data...'))

        iteration_days = 1001 # 1000

        # creating Stock with history
        gold_silver = GoldSilverExchange.objects.create()
        falsify_gold_silver_history(gold_silver, iteration_days)

        # creating tickers & their history
        generate_companies(iteration_days)

        call_events() #calling events

        self.stdout.write(self.style.SUCCESS('Random data generation has been completed'))


def call_events(num=10): # for 10 iterations there will be approximately 6 active events
    for i in range(num):
        events_manager()


def falsify_gold_silver_history(gold_silver, iterations):
    json_path = os.path.join(settings.MEDIA_ROOT, 'gold_silver_rate', f"{gold_silver.id}.json")
    current_time = datetime.datetime.now()
    min_gold_limit, max_gold_limit = 900_000_000, 1_001_000_000

    gold_price = gold_silver.base_price
    affordable_gold = gold_silver.amount
    history = []

    with open(json_path, 'r') as file:
        json_data = json.load(file)

    for i in range(iterations):
        iteration_date = current_time - datetime.timedelta(days=i)
        timestamp = int(iteration_date.timestamp())

        gold_amount_change = random.randint(-400_000, 400_000)
        affordable_gold = max(min_gold_limit, min(max_gold_limit, affordable_gold + gold_amount_change))

        new_gold_price = max(1, (gold_price * (1 + random.uniform(-0.05, 0.05))))

        history.append([new_gold_price, timestamp])

        gold_price = new_gold_price

    json_data["amount"] = affordable_gold
    for info in reversed(history):
        json_data["contents"].append({
            "timestamp": info[1],
            "current price": float(round(info[0], 2))
        })

    with open(json_path, 'w') as file:
        json.dump(json_data, file, indent=2)

    gold_silver.amount = affordable_gold
    gold_silver.current_price = round(history[0][0], 2)
    gold_silver.save()


def falsify_company_history(iteration_days, company):
    current_time = datetime.datetime.now()

    year, month, day = current_time.year, current_time.month, current_time.day
    json_path = os.path.join(settings.MEDIA_ROOT, 'tickers', str(year), str(month), str(day), f"{company.ticker}.json")

    current_time = datetime.datetime.now()
    founding_date = current_time - datetime.timedelta(days=1000)
    affordable_silver = company.silver_reserve
    company_price = float(company.company_price)

    history = []

    json_schema = {
        "ticker": company.ticker,
        "company_type": company.type_id,
        "founding date": int(founding_date.timestamp()),
        "contents": []
    }

    for i in range(iteration_days):
        timestamp = int((current_time - datetime.timedelta(days=i)).timestamp())

        affordable_silver = max(1, (affordable_silver * (1 + random.uniform(-0.05, 0.05))))
        commitment = float(round(Decimal(company.shares_amount * company.share_price * company.dividendes_percent / 100), 2))

        history.append([timestamp, company_price, float(round(affordable_silver, 2)), company.gold_reserve])
        company_price = float(round(affordable_silver - commitment, 2))

    for info in reversed(history):
        json_schema["contents"].append({
            "timestamp": info[0],
            "company_price": info[1],
            "silver_reserve": info[2],
            "gold_reserve": info[3]
        })

    with open(json_path, 'w') as json_file:
        json.dump(json_schema, json_file, indent=2)

    company.save()


def sell_shares_retroactively(user_id, company, amount, price, shares_type, timezone1, timezone2):
    if timezone1 is None and timezone2 is None:
        timestamp = timezone.now() - datetime.timedelta(days=1)
        SharesExchange.objects.create(company=company, amount=amount, price=price, shares_type=shares_type,
                                      owners_right=timestamp, shareholders_right=timestamp, player_id=user_id)
    else:
        SharesExchange.objects.create(company=company, amount=amount, price=price, shares_type=shares_type,
                                      owners_right=timezone1, shareholders_right=timezone2, player_id=user_id)


def generate_companies(iteration_days):
    assets = [
        {"ticker": "TBTA", "name": "Towing Alliance"},
        {"ticker": "TBAEC", "name": "Alpha Electric"},
        {"ticker": "TBAES", "name": "Alto Elevators"},
        {"ticker": "TBASG", "name": "Army Surplus General"},
        {"ticker": "TBBMP", "name": "Blue Mountain Pioneering"},
        {"ticker": "TBBLU", "name": "Builders League United"},
        {"ticker": "TBBBC", "name": "BLU Blast Complex"},
        {"ticker": "TBCR", "name": "Cerveza Royale"},
        {"ticker": "TBCDG", "name": "Chaps Dry Goods"},
        {"ticker": "TBEET", "name": "Elliphany Electric Trains"},
        {"ticker": "TBFAT", "name": "Freeman Airboat Tours"},
        {"ticker": "TBTDFU", "name": "Trench Diggers FIRST UNION"},
        {"ticker": "TBMC", "name": "Mann Co."}
    ]

    for index, asset in enumerate(assets, 1):  # creating users and their tickers
        user = Player.objects.create_user(username=f'djangobot{index}', password=f'djangobot{index}', silver=300000)
        company_type = random.randint(1, 10)
        shares_amount, preferred_shares_amount = random.randint(100, 20000), random.randint(100, 10000)
        new_company = Company.objects.create(type_id=company_type, ticker=asset.get('ticker'), name=asset.get('name'),
                                             shares_amount=shares_amount,
                                             preferred_shares_amount=preferred_shares_amount,
                                             dividendes_percent=random.randint(2, 6))
        PlayerCompanies.objects.create(player=user, company=new_company, shares_amount=shares_amount,
                                       preferred_shares_amount=preferred_shares_amount)

        falsify_company_history(iteration_days, new_company)

        company_ordinary_shares = new_company.shares_amount
        for i in range(1, random.randint(1, 5)):  # sell ordinary shares
            shares_price = random.randint(100, 1000)
            shares_for_sale = random.randint(100, 1000)

            if company_ordinary_shares - shares_for_sale <= 5000:
                break
            company_ordinary_shares -= shares_for_sale

            sell_shares_retroactively(user.id, new_company, shares_for_sale, shares_price, 1, None, None)
