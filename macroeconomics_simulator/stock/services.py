import json
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from stock.models import GoldSilverExchange, Company, Player, PlayerCompanies, CompanyWarehouse, ProductsExchange, \
    AvailableProductsForProduction, CompanyCharacteristics
from stock.utils import CustomException, to_int


def check_object(model: object, condition):
    obj = model.objects.filter(condition).exists()
    if obj:
        return obj
    else:
        raise CustomException(f'{model.__name__} object with selected conditions does not exists')

def get_object(model: object, condition, fields=None): # the best way
    if fields is None:
        fields = []
    obj = model.objects.only(*fields).filter(condition).first()
    if obj is None:
        raise CustomException(f'{model.__name__} object with selected conditions does not exists')
    else:
        return obj

def get_company_inventory(ticker):
    fields = ['amount', 'product', 'company__ticker']
    objects = CompanyWarehouse.objects.only(*fields).filter(company__ticker=ticker)
    return objects


def update_produced_products_amount(ticker):
    company = Company.objects.prefetch_related('companycharacteristics').get(ticker=ticker)
    company_data = company.companycharacteristics
    production_speed = company_data.production_speed
    production_volume = company_data.production_volume
    warehouse_capacity = company_data.warehouse_capacity

    products = CompanyWarehouse.objects.filter(company=company)
    products_for_update = AvailableProductsForProduction.objects.filter(company_type=company.type, product_type__in=products.values_list('product', flat=True))
    updated_products = []
    for product_for_update in products_for_update:
        warehouse = products.get(product=product_for_update.product_type)
        time_now = timezone.now()
        time_difference = time_now - warehouse.check_date
        hours_passed = time_difference.total_seconds() / 3600

        produced_per_hour = 60 * production_speed * production_volume

        total_produced = int(produced_per_hour * hours_passed)

        new_amount = warehouse.amount + total_produced
        remainder = warehouse.remainder or 0

        if new_amount > warehouse_capacity * warehouse.max_amount: # при изменении логики warehouse_capacity!!!
            remainder += new_amount - warehouse.max_amount
            new_amount = warehouse.max_amount

        if remainder > 10000:
            remainder = 10000

        warehouse.amount = new_amount
        warehouse.remainder = remainder
        warehouse.check_date = time_now
        warehouse.save()

        updated_products.append(warehouse)

    return updated_products

def calculate_gold_rice(instance: GoldSilverExchange, amount_of_gold): # | after API, optimize via clickhouse or redis fow webhooks
    affordable_gold = instance.amount
    gold_price = instance.current_price
    base_price = 1000
    fluctuation_level = gold_price * (amount_of_gold / affordable_gold)
    gold_rate = base_price * (100 - fluctuation_level) / 100 # new gold price
    instance.current_price = gold_rate
    #no need for saving data
    return fluctuation_level, gold_rate

def update_gold_price(instance: GoldSilverExchange, amount_of_gold) -> None:
    affordable_gold = instance.amount
    gold_price = instance.current_price
    base_price = 1000
    fluctuation_level = gold_price * (amount_of_gold / affordable_gold)
    gold_rate = base_price * (100 - fluctuation_level) / 100 # new gold price
    instance.current_price = gold_rate
    instance.amount += amount_of_gold
    instance.save() # сделать кастомный save() чтобы записывалась инфа при минимальном изменении в 1 серебрянную монету

def calculate_gold_price(gold_amount):
    current_price = get_object(model=GoldSilverExchange, condition=Q(id=1), fields=['current_price']).current_price
    gold_price = current_price * gold_amount
    return gold_price


def calculate_commitment(company_id=1): # mb change id to something else
    obj = get_object(model=Company, condition=Q(id=company_id), fields=['share_price', 'shares_amount', 'dividendes_percent'])

    obligations = int(obj.shares_amount * obj.share_price * obj.dividendes_percent / 100)
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

def calculate_company_price2(company_income, company_cartoonist, company_gold, company_silver):
    if company_gold > 0:
        current_price = get_object(model=GoldSilverExchange, condition=Q(id=1), fields=['current_price'])
        gold_price = current_price * company_gold
        assets_price = gold_price + company_silver
    else:
        assets_price = company_silver
    company_id = 1
    obj = get_object(model=Company, condition=Q(id=company_id), fields=['share_price', 'shares_amount', 'dividendes_percent'])
    commitment = int(obj.shares_amount * obj.share_price * obj.dividendes_percent / 100)

    company_price = (assets_price + company_income * company_cartoonist) - commitment
    return company_price


def calculate_share_price(company_price, shares_amount):  # | after API, optimize via clickhouse
    share_price = company_price / shares_amount
    return share_price


def calculate_products_price(product_id, products_amount: int):
    stock = get_object(model=ProductsExchange, condition=Q(product_id=product_id), fields=['product', 'sale_price'])
    silver = int(stock.sale_price * products_amount)
    return silver


def get_paginated_objects(model: object, query_params): # later take into account a different limit for each device
    """possible improvement - take into account the passed condition in the filter (when there is a search by name)"""
    page = query_params.get('page')
    limit = query_params.get('limit')
    # add condition if needed
    limit = int(limit) if limit is not None else 10
    page = int(page) if page is not None else 1
    objects = model.objects.all().order_by('-id')
    paginator = Paginator(objects, limit)
    obj = paginator.get_page(page)
    has_next = obj.has_next()

    return obj, has_next


def create_new_company(user_id, request_data):
    company_type = request_data.get('type')
    ticker = request_data.get('ticker')
    name = request_data.get('name')
    shares_amount = request_data.get('shares_amount')
    preferred_shares_amount = request_data.get('preferred_shares_amount')
    dividendes_percent = request_data.get('dividendes_percent')

    check_object(model=Player, condition=Q(id=user_id)) # investigate...

    new_company = Company.objects.create(type_id=company_type, ticker=ticker, name=name, shares_amount=shares_amount,
                                         preferred_shares_amount=preferred_shares_amount, dividendes_percent=dividendes_percent)
    PlayerCompanies.objects.create(player_id=user_id, company=new_company, shares_amount=shares_amount,
                                   preferred_shares_amount=preferred_shares_amount)

    return new_company


def get_player(user_id):
    condition = Q(id=user_id)
    fields = ['username', 'silver', 'gold', 'last_login', 'date_joined']
    player = get_object(model=Player, condition=condition, fields=fields)

    return player


def get_user_companies(user_id):
    fields = ['company__type__type', 'company__ticker', 'company__gold_reserve', 'company__share_price']
    company = PlayerCompanies.objects.select_related('company').filter(player_id=user_id).order_by('-id').only(*fields)

    return company

def get_company_history(ticker):
    obj = get_object(model=Company, condition=Q(ticker=ticker), fields=['history'])
    history = obj.history

    with open(history, 'r') as file:
        history = json.load(file)

    return history


def get_gold_history():
    history = GoldSilverExchange.objects.only('history').first().history

    with open(history, 'r') as file:
        history = json.load(file)

    return history

def purchase_gold(user_id, amount) -> None:
    amount = to_int(amount)
    gold_silver_exchange = GoldSilverExchange.objects.only('current_price', 'amount').first()

    player = get_object(model=Player, condition=Q(id=user_id), fields=['silver', 'gold'])
    player_silver, player_gold = player.silver, player.gold

    current_price = gold_silver_exchange.current_price
    gold_price = current_price * amount

    if player_silver >= gold_price:
        update_gold_price(instance=gold_silver_exchange, amount_of_gold=-amount)

        player_gold += amount
        player.save()
    else:
        raise CustomException(f'Now you have {player_silver} silver, you need {gold_price} silver to buy {amount} gold coins')

def sell_gold(user_id, amount) -> None:
    amount = to_int(amount)
    gold_silver_exchange = GoldSilverExchange.objects.only('current_price', 'amount').first()

    player = get_object(model=Player, condition=Q(id=user_id), fields=['silver', 'gold'])
    player_silver, player_gold = player.silver, player.gold

    if player_gold >= amount:
        update_gold_price(instance=gold_silver_exchange, amount_of_gold=amount)

        player_gold -= amount
        player.save()
    else:
        raise CustomException('You need more gold')


def buy_products(ticker, product_type, amount) -> None:
    amount = to_int(amount)
    company = Company.objects.prefetch_related('companywarehouse').get(ticker=ticker).only('silver_reserve', 'companywarehouse__amount', 'companywarehouse__product')

    if not company:
        raise CustomException(f'Company with ticker {ticker} not found')

    try:
        warehouse = CompanyWarehouse.objects.get(company=company, product__type=product_type)
    except CompanyWarehouse.DoesNotExist: # if there is no warehouse, then create...
        warehouse = CompanyWarehouse.objects.create(company=company, product__type=product_type)
    products_price = calculate_products_price(product_id=warehouse.product.id, products_amount=amount)

    if company.silver_reserve >= products_price:
        warehouse.amount += amount
        company.silver_reserve -= products_price

        company.save(), warehouse.save()

def sell_products(ticker, product_type, amount) -> None:
    amount = to_int(amount)
    company = Company.objects.prefetch_related('companywarehouse').get(ticker=ticker).only('silver_reserve', 'companywarehouse__amount', 'companywarehouse__product')

    if not company:
        raise CustomException(f'Company with ticker {ticker} not found')

    try:
        warehouse = CompanyWarehouse.objects.get(company=company, product__type=product_type)
    except CompanyWarehouse.DoesNotExist:
        raise CustomException(f'Warehouse with product type {product_type} not found for company with ticker {ticker}')

    if warehouse.amount >= amount:
        products_price = calculate_products_price(product_id=warehouse.product.id, products_amount=amount)

        warehouse.amount -= amount
        company.silver_reserve += products_price

        company.save(), warehouse.save()
    else:
        raise CustomException('Company need more products')

