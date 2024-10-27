import json
from decimal import Decimal

from django.db.models import Q

from services.base import get_object
from services.general_services import recalculation_of_the_shareholders_influence
from services.stock.S_services import calculate_products_price
from stock.utils.exceptions import CustomException
from stock.models import Company, CompanyWarehouse, AvailableProductsForProduction, PlayerCompanies, \
    SharesExchange, Player, CompanyRecipe, GoldSilverExchange, ProductType
from django.utils import timezone


def create_new_company(user_id, request_data):
    """
    if the user does not have established tickers, then he establishes it for free, if there is a founded company,
        if he already has a company the price will be equal to the cost of 100 gold in silver
            if user don’t have that kind of money, then ... he lost, let him create a new account
    """
    company_type = request_data.get('type')
    ticker = request_data.get('ticker')
    name = request_data.get('name')
    shares_amount = request_data.get('shares_amount')
    preferred_shares_amount = request_data.get('preferred_shares_amount')
    dividendes_percent = request_data.get('dividendes_percent')

    user = get_object(model=Player, condition=Q(id=user_id), fields=['id', 'silver'])

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
    """available only to the owner of this company, receives goods produced up to the present moment"""

    company = Company.objects.select_related('type').get(ticker=ticker)
    production_speed = company.type.production_speed
    production_volume = company.type.production_volume

    products = CompanyWarehouse.objects.filter(company_id=company.id)
    products_for_update = AvailableProductsForProduction.objects.filter(company_type=company.type, product_type__in=products.values_list('product', flat=True))
    updated_products = []
    for product_for_update in products_for_update:
        warehouse = products.get(product=product_for_update.product_type)
        time_now = timezone.now()
        time_difference = time_now - warehouse.check_date
        hours_passed = time_difference.total_seconds() / 3600

        produced_per_hour = 600 * production_speed * production_volume

        total_produced = int(produced_per_hour * hours_passed)

        new_amount = warehouse.amount + total_produced
        remainder = warehouse.remainder or 0

        if new_amount > warehouse.max_amount: # при изменении логики warehouse_capacity!!!
            remainder += new_amount - warehouse.max_amount
            new_amount = warehouse.max_amount

        if remainder > 50000:
            remainder = 50000

        warehouse.amount = new_amount
        warehouse.remainder = remainder
        warehouse.check_date = time_now
        warehouse.save()

        updated_products.append(warehouse)

    return updated_products


def make_new_shares(user_id, ticker, shares_type, amount, price):
    company = get_object(model=Company, condition=Q(ticker=ticker), fields=['id', 'shares_amount', 'preferred_shares_amount'])
    if shares_type == 1: # ordinary
        company.shares_amount += amount
    else:
        company.preferred_shares_amount += amount

    put_up_shares_for_sale(user_id, company_id=company.id, shares_type=shares_type, amount=amount, price=price)
    company.save()

    if shares_type == 2: # management shares
        recalculation_of_the_shareholders_influence(company_id=company.id)

    return company


def recalculate_shares(obj: PlayerCompanies, shares_type, shares_amount):
    """
    there is no need to recalculate the user's share in the company since this will be done after someone
    buys the user's shares on the stock exchange.
    Now they are on the stock exchange, but the owner is still the one who posted them
    """
    if shares_type == 1:
        obj.shares_amount -= shares_amount
    else: # 2
        obj.preferred_shares_amount -= shares_amount

    if obj.shares_amount == 0 and obj.preferred_shares_amount == 0 and obj.isHead is False:
        obj.delete()
    else:
        obj.save()


def put_up_shares_for_sale(user_id, company_id, shares_type, amount, price):
    """
    depending on the group (company owner, shareholder, or ordinary player) different times will be given to buy back shares
    dividends will also be paid for shares that are listed on the stock exchange
    There will be no opportunity to withdraw shares from the exchange (for now)
    """
    if shares_type == 1:
        condition = Q(player_id=user_id, company_id=company_id, shares_amount__gte=amount)
    else:
        condition = Q(player_id=user_id, company_id=company_id, preferred_shares_amount__gte=amount)
    obj = get_object(model=PlayerCompanies, condition=condition, fields=['shares_amount', 'preferred_shares_amount', 'id', 'isHead'])

    if shares_type == 1: # ordinary
        tz = timezone.now()
        shares = SharesExchange.objects.create(company_id=company_id, amount=amount, price=price, shares_type=shares_type,
                                               owners_right=tz, shareholders_right=tz, player_id=user_id)

        recalculate_shares(obj=obj, shares_type=1, shares_amount=amount)
    elif shares_type == 2: # management
        shares = SharesExchange.objects.create(company_id=company_id, amount=amount, price=price, shares_type=shares_type,
                                               player_id=user_id)

        recalculate_shares(obj=obj, shares_type=2, shares_amount=amount)
    else:
        shares = None
    return shares



def buy_products(ticker, product_type, amount) -> None:
    company = Company.objects.prefetch_related('companywarehouse_set').only('id', 'silver_reserve', 'companywarehouse__amount', 'companywarehouse__product').get(ticker=ticker)

    try:
        warehouse = CompanyWarehouse.objects.select_related(
            'product').get(company_id=company.id, product__type=product_type).only('id', 'amount', 'product__id')

        products_price = calculate_products_price(product_id=warehouse.product_id, products_amount=amount)
    except CompanyWarehouse.DoesNotExist: # if there is no warehouse, then create...
        product = get_object(model=ProductType, condition=Q(type=product_type), fields=['id'])
        warehouse = CompanyWarehouse.objects.create(company_id=company.id, product_id=product.id)

        products_price = calculate_products_price(product_id=warehouse.product.id, products_amount=amount)

    if company.silver_reserve >= products_price:
        warehouse.amount += amount
        company.silver_reserve -= products_price

        company.save(document=True), warehouse.save()

def sell_products(ticker, product_type, amount) -> None:
    company = Company.objects.prefetch_related('companywarehouse_set').only('id', 'silver_reserve', 'companywarehouse__amount', 'companywarehouse__product').get(ticker=ticker)

    try:
        warehouse = CompanyWarehouse.objects.select_related(
            'product').only('id', 'amount', 'product__id').get(company_id=company.id, product__type=product_type)
    except CompanyWarehouse.DoesNotExist:
        raise CustomException(f'Warehouse with product type {product_type} not found for company with ticker {ticker}')

    if warehouse.amount >= amount:
        products_price = calculate_products_price(product_id=warehouse.product_id, products_amount=amount)

        warehouse.amount -= amount
        company.silver_reserve += products_price

        company.save(document=True), warehouse.save()
    else:
        raise CustomException('Company need more products')


def validate_company_recipe(recipe_id, tickers: list):
    """checking the possibility of transmutating a company"""

    company_recipe = CompanyRecipe.objects.select_related('recipe', 'ingredient').filter(recipe_id=recipe_id)
    if len(company_recipe) == 0:
        raise CustomException('Recipe object with selected conditions does not exists')

    if company_recipe[0].recipe.isAvailable: # recipe may not be available due to certain events
        # print(len(tickers), sum([obj.amount for obj in company_recipe]), tickers, company_recipe)
        if len(tickers) == sum([obj.amount for obj in company_recipe]):
            user_companies = []
            for ticker in tickers:
                company = get_object(model=Company, condition=Q(ticker=ticker))
                user_companies.append(company)

            final_company_types_for_transmutation = []
            for obj in company_recipe:
                for i in range(obj.amount):
                    final_company_types_for_transmutation.append(obj.ingredient.type)

            for company in user_companies:
                if company.type_id in final_company_types_for_transmutation:
                    final_company_types_for_transmutation.remove(company.type_id)
                else:
                    raise CustomException('Wrong type of company was transferred for transmutation using a specific recipe')

            #clearing the exchange
            SharesExchange.objects.filter(company__in=user_companies).delete()

            return user_companies, company_recipe[0].recipe.company_type
        else:
            raise CustomException(f'The number of companies required for transmutation does not correspond to those transferred')
    else:
        raise CustomException(f'Recipe with id {recipe_id} not available now')


def transmutate_company(user_id, companies, name, ticker, company_type, dividendes):
    shares_amount, preferred_shares_amount = 100_000_0, 100_000_0 # probably default value

    general_silver = Decimal(sum([company.silver_reserve for company in companies]))
    general_gold = sum([company.gold_reserve for company in companies])

    new_company = Company.objects.create(type_id=company_type, ticker=ticker, name=name, shares_amount=shares_amount,
                                         silver_reserve=general_silver, gold_reserve=general_gold,
                                         preferred_shares_amount=preferred_shares_amount, dividendes_percent=dividendes)

    distribution_of_company_shares(user_id, companies, new_company, shares_amount, preferred_shares_amount)


def distribution_of_company_shares(user_id, companies, new_company, new_shares_amount, new_preferred_shares_amount):
    total_shares, total_preferred_shares = 0, 0
    player_share_map = {}

    for company in companies:
        shareholders = PlayerCompanies.objects.filter(company_id=company.id).only('player__id', 'shares_amount', 'preferred_shares_amount')

        total_shares += company.shares_amount
        total_preferred_shares += company.preferred_shares_amount

        for shareholder in shareholders:
            if shareholder.player_id not in player_share_map:
                player_share_map[shareholder.player_id] = {
                    'shares': 0,
                    'preferred_shares': 0,
                }

            player_share_map[shareholder.player_id]['shares'] += shareholder.shares_amount
            player_share_map[shareholder.player_id]['preferred_shares'] += shareholder.preferred_shares_amount

    new_shareholders = []
    for player_id, share_info in player_share_map.items(): # recalculation of shareholders' shares
        new_player_shares = (share_info['shares'] / total_shares) * new_shares_amount if total_shares > 0 else 0
        new_player_pshares = (share_info['preferred_shares'] / total_preferred_shares) * new_preferred_shares_amount if total_preferred_shares > 0 else 0

        new_shareholders.append(PlayerCompanies(
            player_id=player_id, company=new_company, shares_amount=new_player_shares,
            preferred_shares_amount=new_player_pshares, isFounder=False, isHead=False
        ))

    PlayerCompanies.objects.bulk_create(new_shareholders)

    #clearing outdated shares
    PlayerCompanies.objects.filter(company__in=companies).delete()

    #warehouse demolition - no need for improvement for now
    CompanyWarehouse.objects.filter(company__in=companies).delete()

    #destruction of companies | in the future possible let them be, but silenced
    Company.objects.filter(ticker__in=[company.ticker for company in companies]).delete()

    PlayerCompanies.objects.update_or_create(player_id=user_id, company=new_company, defaults={'isFounder': True, 'isHead': True})


def merge_companies(user_id, validated_data):
    tickers = validated_data.get('tickers')
    recipe_id = validated_data.get('recipe_id')
    name = validated_data.get('name')
    ticker = validated_data.get('ticker')
    dividendes_percent = validated_data.get('dividendes_percent')

    user_companies, company_type = validate_company_recipe(recipe_id, tickers)

    transmutate_company(user_id, user_companies, name, ticker, company_type, dividendes_percent)


def get_company_history(ticker):
    obj = get_object(model=Company, condition=Q(ticker=ticker), fields=['history'])
    history = obj.history

    with open(history, 'r') as file:
        history = json.load(file)

    return history

def get_top_companies(amount=10):
    top = Company.objects.all().order_by('-company_price').values(
        'ticker', 'name', 'company_price', 'daily_company_price', 'dividendes_percent', 'founding_date')[:amount]
    return top


def get_available_recipes():
    recipes = CompanyRecipe.objects.select_related("recipe", "ingredient").filter(recipe__isAvailable=True)

    return recipes
