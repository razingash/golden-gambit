import json
from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from services.base import get_object, get_object_or_create
from services.general_services import recalculation_of_the_shareholders_influence
from stock.models import GoldSilverExchange, SharesExchange, PlayerCompanies, Player, Company, ProductsExchange, \
    SharesWholesaleTrade
from stock.utils import CustomException, to_int, SharesTypes


def update_gold_price(instance: GoldSilverExchange, amount_of_gold) -> None:
    affordable_gold = instance.amount
    gold_price = float(round(instance.current_price, 2))
    base_price = 1000
    fluctuation_level = gold_price * (amount_of_gold / affordable_gold)
    gold_rate = base_price * (100 - fluctuation_level) / 100 # new gold price
    instance.current_price = gold_rate
    instance.amount += amount_of_gold
    instance.save() # сделать кастомный save() чтобы записывалась инфа при минимальном изменении в 1 серебрянную монету


def calculate_gold_price(gold_amount):
    current_price = get_object(model=GoldSilverExchange, condition=Q(id=1), fields=['current_price']).current_price
    gold_price = float(round(current_price * gold_amount, 2))
    return gold_price


def calculate_products_price(product_id, products_amount: int):
    stock = get_object(model=ProductsExchange, condition=Q(product_id=product_id), fields=['product', 'sale_price'])
    silver = int(stock.sale_price * products_amount)
    return silver


def get_available_shares_for_everyone(current_time): # unlogged users
    objects = SharesExchange.objects.filter(shareholders_right__lt=current_time).order_by('-id')

    return objects

def get_availabale_shares_for_shareholders(current_time, user_id): # logged users | shareholders
    user_companies = PlayerCompanies.objects.filter(player_id=user_id).values_list('company_id', flat=True)
    objects = SharesExchange.objects.filter(company__in=user_companies, owners_right__lt=current_time).order_by('-id')

    return objects

def get_available_shares_for_owners(user_id): # logged users | owners
    user_companies = PlayerCompanies.objects.filter(player_id=user_id, isHead=True).values_list('company_id', flat=True)
    objects = SharesExchange.objects.filter(company__in=user_companies).order_by('-id')

    return objects

def get_available_shares(query_params, user_id=None):
    availability = query_params.get('availability')  # availability=1
    page = query_params.get('page')
    limit = query_params.get('limit')
    # add condition if needed
    limit = int(limit) if limit is not None else 10
    page = int(page) if page is not None else 1
    if user_id is None:
        current_time = timezone.now()
        objects = get_available_shares_for_everyone(current_time)
    else:
        if availability is None: # ordinary shares
            current_time = timezone.now()
            objects = get_availabale_shares_for_shareholders(current_time, user_id)
        else: # 1 - management shares
            objects = get_available_shares_for_owners(user_id)

    paginator = Paginator(objects, limit)
    obj = paginator.get_page(page)
    has_next = obj.has_next()

    return obj, has_next


def buy_shares(user_id, ticker, amount, price): # for silver
    """buys company shares in a certain quantity at a fixed price"""
    company = get_object(model=Company, condition=Q(ticker=ticker))
    stock_shares = get_object(model=SharesExchange, condition=Q(company=company))
    user = get_object(model=Player, condition=Q(id=user_id))
    company = get_object(model=Company, condition=Q(ticker=ticker))

    full_price = int(amount * price)


    if user.silver >= full_price:
        if stock_shares.amount >= amount:
            user.silver -= full_price
            company.silver_reserve += full_price
            stock_shares.amount -= amount

            if stock_shares.amount == amount:
                stock_shares.delete()
            else:
                stock_shares.save()

            company.save(document=True), user.save()
        else:
            raise CustomException(f'The current number of shares on the exchange is {stock_shares.amount}, you need {amount}')
    else:
        raise CustomException('You need more silver')

def buy_management_shares(user_id, ticker, amount, price):
    """buys company shares in a certain quantity at a fixed price"""
    company = get_object(model=Company, condition=Q(ticker=ticker))
    stock_shares = get_object(model=SharesExchange, condition=Q(company=company))
    user = get_object(model=Player, condition=Q(id=user_id))
    company = get_object(model=Company, condition=Q(ticker=ticker))

    full_price = int(amount * price)

    if user.gold >= full_price:
        if stock_shares.amount >= amount:
            user.gold -= full_price
            company.gold_reserve += full_price
            stock_shares.amount -= amount

            if stock_shares.amount == amount:
                stock_shares.delete()
            else:
                stock_shares.save()

            company.save(document=True), user.save()
        else:
            raise CustomException(f'The current number of shares on the exchange is {stock_shares.amount}, you need {amount}')
    else:
        raise CustomException('You need more gold')


def buy_shares_wholesale(user_id, ticker, amount, offered_money, shares_type):
    """
    buys company shares in a certain quantity within a given price.
    offered_money is the money that the user is willing to give for a specific number of shares.
    shares will be purchased with available (transferred) money.
    """
    company = get_object(model=Company, condition=Q(ticker=ticker))
    user = get_object(model=Player, condition=Q(id=user_id))

    if shares_type == 1: # ordinary
        shares_type = SharesTypes.ORDINARY
        user_money = user.silver
    elif shares_type == 2: # preffered
        shares_type = SharesTypes.PREFERRED
        user_money = user.gold
    else:
        raise CustomException('Error in buy_shares_wholesale due to incorrect sharesType')

    stock_shares_lots = SharesExchange.objects.filter(company=company, shares_type=shares_type).order_by('price')

    if user_money >= offered_money:
        total_purchased = 0
        total_paid = Decimal('0.00')

        remaining_money = Decimal(offered_money)
        remaining_amount = amount

        for lot in stock_shares_lots:
            if remaining_amount <= 0 or remaining_money <= 0:
                break

            available_shares = min(remaining_amount, lot.amount)
            total_cost_for_lot = Decimal(available_shares) * Decimal(lot.price)

            if total_cost_for_lot <= remaining_money:
                total_purchased += available_shares
                total_paid += total_cost_for_lot
                remaining_money -= total_cost_for_lot
                remaining_amount -= available_shares

                lot.amount -= available_shares
                lot.save()

            else:
                max_affordable_shares = int(remaining_money // Decimal(lot.price))
                total_purchased += max_affordable_shares
                total_paid += Decimal(max_affordable_shares) * Decimal(lot.price)
                remaining_money -= Decimal(max_affordable_shares) * Decimal(lot.price)
                remaining_amount -= max_affordable_shares

                lot.amount -= max_affordable_shares
                lot.save()

                break

        if total_purchased == 0:
            raise CustomException("Not enough funds to buy any shares or no shares available.")

        transaction = SharesWholesaleTrade.objects.create(company=company, reserved_money=offered_money, paid=total_paid,
                                                          desired_quantity=amount, shares_type=shares_type, buyer=user,
                                                          purchased=total_purchased)

        if shares_type == 1: # ordinary
            obj, is_created = get_object_or_create(model=PlayerCompanies, condition=Q(player_id=user_id, company=company),
                                                   condtion_create={'player_id': user_id, 'company': company,
                                                                    'isFounder': False, 'shares_amount': total_purchased,
                                                                    'isHead': False, 'preferred_shares_amount': 0})
            if not is_created:
                obj.shares_amount += total_purchased
                obj.save()
            company.shares_amount -= total_purchased
            company.silver_reserve += total_paid
            user.silver -= total_paid
            company.save(document=True), user.save()
        elif shares_type == 2: # preffered
            obj, is_created = get_object_or_create(model=PlayerCompanies, condition=Q(player_id=user_id, company=company),
                                                   condtion_create={'player_id': user_id, 'company': company,
                                                                    'isFounder': False, 'isHead': False, 'shares_amount': 0,
                                                                    'preferred_shares_amount': total_purchased})
            if not is_created:
                obj.preferred_shares_amount += total_purchased
                obj.save()

            recalculation_of_the_shareholders_influence(company)

            company.shares_amount -= total_purchased
            company.gold_reserve += total_paid
            user.gold -= total_paid
            company.save(document=True), user.save()

        return transaction
    else:
        raise CustomException("You don't have that much money")



def purchase_gold(user_id, amount) -> None:
    amount = to_int(amount)
    gold_silver_exchange = GoldSilverExchange.objects.only('current_price', 'amount').first()

    player = get_object(model=Player, condition=Q(id=user_id), fields=['silver', 'gold'])

    current_price = gold_silver_exchange.current_price
    gold_price = current_price * amount

    if player.silver >= gold_price:
        update_gold_price(instance=gold_silver_exchange, amount_of_gold=-amount)

        player.silver -= gold_price
        player.gold += amount
        player.save()
    else:
        raise CustomException(f'Now you have {player.silver} silver, you need {gold_price} silver to buy {amount} gold coins')

def sell_gold(user_id, amount) -> None:
    amount = to_int(amount)
    gold_silver_exchange = GoldSilverExchange.objects.only('current_price', 'amount').first()

    player = get_object(model=Player, condition=Q(id=user_id), fields=['silver', 'gold'])

    current_price = gold_silver_exchange.current_price
    gold_price = current_price * amount

    if player.gold >= amount:
        update_gold_price(instance=gold_silver_exchange, amount_of_gold=amount)

        player.silver += gold_price
        player.gold -= amount
        player.save()
    else:
        raise CustomException('You need more gold')


def get_gold_history():
    history = GoldSilverExchange.objects.only('history').first().history

    with open(history, 'r') as file:
        history = json.load(file)

    return history
