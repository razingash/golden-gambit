from django.core.paginator import Paginator
from django.db.models import Q
from stock.models import GoldSilverExchange, Company, Player, PlayerCompanies, StateLaw, GlobalEvent
from stock.utils import CustomException


def check_object(model: object, condition):
    obj = model.objects.filter(condition).exists()
    if obj:
        return True
    else:
        raise CustomException(f'{model.__name__} object with selected conditions does not exists')

def get_object(model: object, condition, fields=None): # не сейчас но позже может быть ошибка с полями(когда дойдет до patch)
    obj = model.objects.only(*fields).filter(condition).first()
    if obj is None:
        raise CustomException(f'{model.__name__} object with selected conditions does not exists')
    else:
        return obj



def calculate_gold_rate(purchased_gold, model): # | after API, optimize via clickhouse or redis
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


def get_paginated_objects(model: object, query_params): # later take into account a different limit for each device
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
