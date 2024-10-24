import json

from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.db.models import Sum, F, Value

from services.stock.S_services import calculate_gold_price
from stock.models import GoldSilverExchange, Company, CompanyWarehouse, Player

"""
after API, optimize via clickhouse or redis fow webhooks
"""
async def get_current_gold_silver_rate(): # redis
    cached_rate = cache.get('gold_silver_rate')

    if cached_rate:
        rate = json.loads(cached_rate)
    else:
        rate = await GoldSilverExchange.objects.only('current_price', 'amount').afirst()
        cache.set('gold_silver_rate', json.dumps(rate.to_dict()), timeout=5)
    return rate

@sync_to_async(thread_sensitive=False)
def get_top_users_wealth(amount=10): # найти способ передавать gold_price_obj  в одном запросе с этим
    gold_price_obj = GoldSilverExchange.objects.only('current_price').first()
    current_gold_price = gold_price_obj.current_price if gold_price_obj else 0

    users = Player.objects.annotate(
        converted_gold=F('gold') * Value(current_gold_price),
        wealth=F('silver') + F('gold') * Value(current_gold_price)
    ).order_by('-wealth')[:amount]

    return list(users)

@sync_to_async(thread_sensitive=False)
def get_top_companies_wealth(amount=10):
    top = Company.objects.all().order_by('-company_price')[:amount]

    return list(top)


"""Perhaps these functions will be needed when creating bots"""
def calculate_company_price(instance: Company): # company_income
    assets_price = calculate_assets_price(instance.gold_reserve, instance.silver_reserve)
    commitment = calculate_commitment(instance)
    company_income = calculate_company_income(instance.id)

    company_price = (assets_price + company_income) - commitment
    return company_price

def calculate_commitment(company: Company): # mb change id to something else
    obligations = int(company.shares_amount * company.share_price * company.dividendes_percent / 100)
    return obligations

def calculate_assets_price(company_gold, company_silver):
    if company_gold > 0:
        gold_price = calculate_gold_price(company_gold) # optimize later
        assets_price = gold_price + company_silver
    else:
        assets_price = company_silver
    return assets_price

def calculate_company_income(company_id):
    warehouses = CompanyWarehouse.objects.filter(company_id=company_id).annotate(
        sale_price=F('product__productsexchange__sale_price')).aggregate(
        company_income=Sum(F('amount') * F('sale_price'))
    )
    company_income = warehouses['company_income'] if warehouses['company_income'] is not None else 0
    return company_income

