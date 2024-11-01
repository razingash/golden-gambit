import random

from django.db.models import ExpressionWrapper, IntegerField, F

from services.company.C_services import update_produced_products_amount
from services.simulation.actions import *
from stock.models import Player, GoldSilverExchange, PlayerCompanies, ProductsExchange, CompanyWarehouse

""" later remove these services and associated tasks"""

def simulation_manager():
    """selects a random user to trigger the action"""
    users = Player.objects.filter(id__lte=13)
    random_user = users[random.randint(0, len(users)-1)]

    simulation_orchestrator(random_user)


def simulation_orchestrator(user: Player):
    """selects which action to run for a specific user"""
    choices = [-1, 0, 1]
    weights = [2, 1, 2]
    expedience = random.choices(choices, weights)[0]

    if expedience > 0:
        simulation_operator_profitable(user, expedience)
    elif expedience < 0:
        simulation_operator_unprofitable(user, expedience)
    else:
        simulation_operator_default(user)


def simulation_operator_profitable(user: Player, expedience: int): # expedience > 0
    """available actions:
    {1: [action_buy_cheap_products, action_sell_expensive_products]}
    """
    user_silver, user_gold = user.silver, user.gold

    action = random.randint(1, 2)
    user_company = get_first_user_company(user.id).company
    if user_company:
        if action == 1: # buys the most cheap product
            product = ProductsExchange.objects.select_related('product').annotate(
                difference=ExpressionWrapper(
                    F('purchase_price') - F('product__base_price') * 10, output_field=IntegerField()
                )
            ).order_by('difference').first()
            if product.difference > 0:
                maximum_purchase = int(user_silver / product.purchase_price / 4)
                if maximum_purchase > 1:
                    get_produced_products(user_company.ticker)

                    amount = random.randint(1, maximum_purchase)
                    action_buy_cheap_products(company_ticker=user_company.ticker, amount=amount,
                                              product_type=product.product.type)
        else: # sells the most expensive product
            warehouse = CompanyWarehouse.objects.select_related('product').filter(company=user_company).annotate(
                profit_difference=ExpressionWrapper(
                    F('product__productsexchange__sale_price') - F('product__productsexchange__purchase_price'),
                    output_field=IntegerField()
                )
            ).order_by('profit_difference').first()
            if warehouse.amount > 200:
                amount = random.randint(100, warehouse.amount)
                action_sell_expensive_products(company_ticker=user_company.ticker, amount=amount,
                                               product_type=warehouse.product.type)


def simulation_operator_unprofitable(user: Player, expedience: int): # expedience < 0
    """
    available actions: {-1: [buy_expensive_products, action_sell_cheap_products, action_sell_shares]}
    """
    user_silver, user_gold = user.silver, user.gold
    action = random.randint(1, 2)
    user_company = get_first_user_company(user.id).company
    if user_company:
        if action == 1: # buys the most expensive product or the usual one (if there are no events)
            product = ProductsExchange.objects.select_related('product').annotate(
                difference=ExpressionWrapper(
                    F('purchase_price') - F('product__base_price') * 10, output_field=IntegerField()
                )
            ).order_by('-difference').first()
            if product.difference == 0: # buy random product
                get_produced_products(user_company.ticker)

                products = ProductsExchange.objects.all().only('purchase_price')
                random_product = products[random.randint(0, len(products)-1)]
                maximum_purchase = int(user_silver / random_product.purchase_price / 4)
                if maximum_purchase > 1:
                    amount = random.randint(1, maximum_purchase)
                    action_buy_expensive_products(company_ticker=user_company.ticker, amount=amount,
                                                  product_type=product.product.type)
            else: # buy expensive product
                maximum_purchase = int(user_silver / product.purchase_price / 4)
                if maximum_purchase > 1:
                    get_produced_products(user_company.ticker)

                    amount = random.randint(1, maximum_purchase)
                    action_buy_expensive_products(company_ticker=user_company.ticker, amount=amount,
                                                  product_type=product.product.type)
        else: # sells the cheapest product available
            warehouse = CompanyWarehouse.objects.select_related('product').filter(company=user_company).annotate(
                profit_difference=ExpressionWrapper(
                    F('product__productsexchange__sale_price') - F('product__productsexchange__purchase_price'),
                    output_field=IntegerField()
                )
            ).order_by('-profit_difference').first()
            if warehouse.amount > 200:
                amount = random.randint(100, warehouse.amount)
                action_sell_cheap_products(company_ticker=user_company.ticker, amount=amount,
                                           product_type=warehouse.product.type)


def simulation_operator_default(user: Player): # expedience = 0
    """available actions: [action_do_nothing, action_buy_gold, action_sell_gold]"""
    gold_rate = GoldSilverExchange.objects.first()
    gold_price, gold_amount = gold_rate.current_price, gold_rate.amount
    user_silver, user_gold = user.silver, user.gold
    action = random.randint(1, 3)

    if action == 1: # buy gold if user have enough silver
        maximum_purchase = int(user_silver / gold_price / 2)
        if maximum_purchase > 1:
            amount = random.randint(1, maximum_purchase)
            action_buy_gold(user.id, amount)
    elif action == 2: # sell gold if user have enough
        maximum_sale = int(user_gold / 5)
        if maximum_sale > 1:
            action_sell_gold(user.id, maximum_sale)


def get_first_user_company(player_id): # обработать случай если компаний нет
    company = PlayerCompanies.objects.select_related('company').filter(player_id=player_id, isHead=True).first()

    return company


def get_produced_products(ticker) -> None:
    """"updates company goods quantity"""
    update_produced_products_amount(ticker)
