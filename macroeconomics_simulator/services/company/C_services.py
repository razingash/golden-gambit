import json

from django.db.models import Q

from services.base import get_object
from services.general_services import recalculation_of_the_shareholders_influence
from services.stock.S_services import calculate_products_price
from stock.models import Company, CompanyWarehouse, AvailableProductsForProduction, PlayerCompanies, \
    SharesExchange, Player, CompanyRecipe, GoldSilverExchange, ProductType
from django.utils import timezone

from stock.utils import to_int, CustomException


def create_new_company(user_id, request_data):
    """
    if the user does not have established companies, then he establishes it for free, if there is a founded company,
        if he already has a company the price will be equal to the cost of 100 gold in silver
            if user don’t have that kind of money, then ...
    """
    company_type = request_data.get('type')
    ticker = request_data.get('ticker')
    name = request_data.get('name')
    shares_amount = request_data.get('shares_amount')
    preferred_shares_amount = request_data.get('preferred_shares_amount')
    dividendes_percent = request_data.get('dividendes_percent')

    user = get_object(model=Player, condition=Q(id=user_id))

    if not PlayerCompanies.objects.filter(player_id=user_id, isFounder=True).exists():
        pass
    else: # 100 is amount of gold
        stock_gold_price = get_object(model=GoldSilverExchange, condition=Q(base_price=1000),
                                      fields=['current_price']).current_price
        company_opening_price = 100 * stock_gold_price
        if user.silver >= company_opening_price:
            user.silver -= company_opening_price
            user.save()
        else:
            raise CustomException('You need more money to open new company')

    new_company = Company.objects.create(type_id=company_type, ticker=ticker, name=name, shares_amount=shares_amount,
                                         preferred_shares_amount=preferred_shares_amount, dividendes_percent=dividendes_percent)
    PlayerCompanies.objects.create(player_id=user_id, company=new_company, shares_amount=shares_amount,
                                   preferred_shares_amount=preferred_shares_amount)

    return new_company

def get_company_inventory(ticker):
    objects = CompanyWarehouse.objects.select_related('company').only('amount', 'product', 'company__ticker').filter(company__ticker=ticker)
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


def calculate_share_price(company_price, shares_amount):  # | after API, optimize via clickhouse
    share_price = company_price / shares_amount
    return share_price


def make_new_shares(ticker, shares_type, amount, price): # improve? (now it works strange... or not?)
    amount, price = to_int(amount), to_int(price)
    company = get_object(model=Company, condition=Q(ticker=ticker))
    company.shares_amount += amount
    SharesExchange.objects.create(company=company, shares_type=shares_type, amount=amount, price=price)

    if shares_type == 2: # management shares
        recalculation_of_the_shareholders_influence(company)

    company.save()
    return company


def put_up_shares_for_sale(company, shares_type, amount, price):
    if shares_type == 1: # ordinary
        tz = timezone.now()
        shares = SharesExchange.objects.create(company=company, amount=amount, price=price, shares_type=shares_type,
                                               owners_right=tz, shareholders_right=tz)
    elif shares_type == 2: # management
        shares = SharesExchange.objects.create(company=company, amount=amount, price=price, shares_type=shares_type)
    else:
        shares = None
    return shares



def buy_products(ticker, product_type, amount) -> None:
    amount = to_int(amount)
    company = Company.objects.prefetch_related('companywarehouse_set').only('silver_reserve', 'companywarehouse__amount', 'companywarehouse__product').get(ticker=ticker)

    try:
        warehouse = CompanyWarehouse.objects.get(company=company, product__type=product_type)
    except CompanyWarehouse.DoesNotExist: # if there is no warehouse, then create...
        product = ProductType.objects.get(type=product_type)
        warehouse = CompanyWarehouse.objects.create(company=company, product=product)
    products_price = calculate_products_price(product_id=warehouse.product.id, products_amount=amount)

    if company.silver_reserve >= products_price:
        warehouse.amount += amount
        company.silver_reserve -= products_price

        company.save(document=True), warehouse.save()

def sell_products(ticker, product_type, amount) -> None:
    amount = to_int(amount)
    company = Company.objects.prefetch_related('companywarehouse_set').only('silver_reserve', 'companywarehouse__amount', 'companywarehouse__product').get(ticker=ticker)

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

        company.save(document=True), warehouse.save()
    else:
        raise CustomException('Company need more products')


def get_company_history(ticker):
    obj = get_object(model=Company, condition=Q(ticker=ticker), fields=['history'])
    history = obj.history

    with open(history, 'r') as file:
        history = json.load(file)

    return history

def get_top_companies(amount=10):
    top = Company.objects.all().order_by('-company_price').values('ticker', 'name', 'company_price',
                                                                  'dividendes_percent', 'founding_date')[:amount]
    return top


def get_available_recipes():
    recipes = CompanyRecipe.objects.select_related("recipe", "ingredient").filter(recipe__isAvailable=True)

    return recipes
