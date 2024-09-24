from django.db.models import Q
from stock.models import GoldSilverExchange, Company


def get_object(model: object, condition, fields):
    obj = model.objects.get(condition).only(*fields)
    return obj



def calculate_gold_rate(purchased_gold): # | after API, optimize via clickhouse or redis
    obj = get_object(model=GoldSilverExchange, condition=Q(id=1), fields=['current_price', 'amount']) #no need in base_price
    affordable_gold = obj.amount
    gold_price = obj.current_price
    base_price = 1000
    fluctuation_level = gold_price * (purchased_gold / affordable_gold)
    gold_rate = base_price * (100 - fluctuation_level) / 100
    return fluctuation_level, gold_rate


def calculate_gold_price(gold_amount):
    current_price = get_object(model=GoldSilverExchange, condition=Q(id=1), fields=['current_price'])
    gold_price = current_price * gold_amount
    return gold_price


def calculate_commitment(company_id=1): # mb change id to something else
    obj = get_object(model=Company, condition=Q(id=company_id), fields=['shares_price', 'shares_amount', 'dividendes_percent'])

    obligations = int(obj.shares_amount * obj.shares_price * obj.dividendes_percent / 100)
    return obligations

#not includes products, later improve(mb add new function)
def calculate_assets_price(company_gold, company_silver): # | after API, optimize via clickhouse #золото + серебро + минимальная стоимость имеющихся продуктов
    if company_gold > 0:
        gold_price = calculate_gold_price(company_gold)
        assets_price = gold_price + company_silver
    else:
        assets_price = company_silver
    return assets_price


def calculate_company_price(company_income, company_cartoonist, company_gold, company_silver): # | after API, optimize via clickhouse
    assets_price = calculate_assets_price(company_gold, company_silver)
    commitment = calculate_commitment()
    company_price = (assets_price + company_income * company_cartoonist) - commitment
    return company_price


def calculate_share_price(company_price, shares_amount):  # | after API, optimize via clickhouse
    share_price = company_price / shares_amount
    return share_price

