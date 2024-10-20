import json

from channels.layers import get_channel_layer
from django.core.cache import cache
from django.db.models import Q, Sum, F, Value

from services.base import get_object
from services.stock.S_services import calculate_gold_price
from stock.models import GoldSilverExchange, Company, CompanyWarehouse, Player


async def get_current_gold_silver_rate():
    cached_rate = cache.get('gold_silver_rate')

    if cached_rate:
        rate = json.loads(cached_rate)
    else:
        rate = await GoldSilverExchange.objects.only('current_price', 'amount').afirst()
        cache.set('gold_silver_rate', json.dumps(rate.to_dict()), timeout=5)
    return rate

async def get_user_wealth(player_id): # once per minute or...
    """probably make another function to get data about multiple users at once?"""
    gold_price_obj = await GoldSilverExchange.objects.only('current_price').afirst()
    current_gold_price = gold_price_obj.current_price if gold_price_obj else 0

    user = await Player.objects.annotate(
        converted_gold=F('gold') * Value(current_gold_price), wealth=F('silver') + F('gold') * Value(current_gold_price)
    ).aget(id=player_id)

    return user

"""
after API, optimize via clickhouse or redis fow webhooks
"""

def fast_calculate_gold_price(instance: GoldSilverExchange, amount_of_gold):
    affordable_gold = instance.amount
    gold_price = instance.current_price
    base_price = 1000
    fluctuation_level = gold_price * (amount_of_gold / affordable_gold)
    gold_rate = base_price * (100 - fluctuation_level) / 100 # new gold price
    instance.current_price = gold_rate
    #no need for saving data
    return fluctuation_level, gold_rate


"""Most likely the webhook for the functions below won't be useful"""
def calculate_commitment(company_id=1): # mb change id to something else
    obj = get_object(model=Company, condition=Q(id=company_id), fields=['share_price', 'shares_amount', 'dividendes_percent'])

    obligations = int(obj.shares_amount * obj.share_price * obj.dividendes_percent / 100)
    return obligations

def calculate_assets_price(company_gold, company_silver):
    if company_gold > 0:
        gold_price = calculate_gold_price(company_gold)
        assets_price = gold_price + company_silver
    else:
        assets_price = company_silver
    return assets_price

def calculate_company_income(company_instance):
    warehouses = CompanyWarehouse.objects.filter(company=company_instance).annotate(
        sale_price=F('product__productsexchange__sale_price')).aggregate(
        company_income=Sum(F('amount') * F('sale_price'))
    )
    company_income = warehouses['company_income'] if warehouses['company_income'] is not None else 0
    return company_income

def calculate_company_price(company_income, company_gold, company_silver):
    assets_price = calculate_assets_price(company_gold, company_silver)
    commitment = calculate_commitment()
    company_price = (assets_price + company_income) - commitment
    return company_price

def calculate_share_price(company_price, shares_amount):  # | after API, optimize via clickhouse
    share_price = company_price / shares_amount
    return share_price
