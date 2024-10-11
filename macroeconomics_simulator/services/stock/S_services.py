import json
from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Q, Subquery, OuterRef, Sum, Min
from django.utils import timezone

from services.base import get_object, get_object_or_create, paginate_objects
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


def get_available_company_shares_for_everyone(ticker, current_time): # unlogged users
    objects = SharesExchange.objects.filter(company__ticker=ticker, shareholders_right__lt=current_time).order_by('price')

    return objects

def get_availabale_company_shares_for_shareholders(ticker, current_time, user_id): # logged users | shareholders
    user_company = PlayerCompanies.objects.filter(company__ticker=ticker,
                                                  player_id=user_id).values_list('company_id', flat=True)

    if user_company.exists():
        objects = SharesExchange.objects.filter(company_id=user_company.first(), owners_right__lt=current_time).order_by('price')
    else:
        objects = get_available_company_shares_for_everyone(ticker, current_time)

    return objects

def get_available_company_shares_for_owners(ticker, user_id): # logged users | owners
    user_company = PlayerCompanies.objects.filter(company__ticker=ticker,
                                                  player_id=user_id, isHead=True).values_list('company_id', flat=True)

    if user_company.exists():
        objects = SharesExchange.objects.filter(company=user_company.first()).order_by('price')
    else:
        objects = []

    return objects

def get_available_company_shares(query_params, ticker, user_id=None):
    page = query_params.get('page')
    limit = query_params.get('limit')
    # add condition if needed
    limit = int(limit) if limit is not None else 10
    page = int(page) if page is not None else 1
    if user_id is None:
        current_time = timezone.now()
        objects = get_available_company_shares_for_everyone(ticker, current_time)
    else:
        if not PlayerCompanies.objects.filter(company__ticker=ticker, player_id=user_id, isHead=True).exists():
            current_time = timezone.now()
            objects = get_availabale_company_shares_for_shareholders(ticker, current_time, user_id)
        else:
            objects = get_available_company_shares_for_owners(ticker, user_id)

    paginator = Paginator(objects, limit)
    obj = paginator.get_page(page)
    has_next = obj.has_next()

    return obj, has_next


def get_shares_on_stock_for_wholesale(query_params):
    min_price_subquery = SharesExchange.objects.filter(
        company=OuterRef('company'),
        shares_type=OuterRef('shares_type')
    ).order_by('price').values('price')[:1]

    shares_with_aggregates = SharesExchange.objects.values(
        'company__ticker', 'company__name', 'shares_type'
    ).annotate(total_amount=Sum('amount'),
               min_price=Min('price')).filter(min_price=Subquery(min_price_subquery)).order_by('company', 'shares_type')

    obj, has_next = paginate_objects(shares_with_aggregates, query_params)
    return obj, has_next


def buy_shares(user_id, ticker, amount, price, pk): # for silver
    """buys company shares in a certain quantity at a fixed price"""
    company = get_object(model=Company, condition=Q(ticker=ticker))
    stock_shares = get_object(model=SharesExchange, condition=Q(company_id=company.id, id=pk))
    user = get_object(model=Player, condition=Q(id=user_id))

    amount = to_int(amount)
    price = to_int(price)
    full_price = amount * price

    if user.silver >= full_price:
        if stock_shares.amount >= amount:
            head_of_company = get_object(model=PlayerCompanies, condition=Q(company_id=company.id, isHead=True))

            if stock_shares.player.id == head_of_company.player.id: # if seller is head of the company then all funds will go to the company
                company.silver_reserve += full_price
                company.save(document=True)
            else: # otherwise funds will go to the seller
                stock_shares.player.silver += full_price
                stock_shares.player.save()

            user.silver -= full_price
            stock_shares.amount -= amount
            head_of_company.shares_amount -= amount
            if stock_shares.amount <= amount:
                stock_shares.delete()
            else:
                stock_shares.save()

            head_of_company.save(), user.save()

            get_object_or_create(PlayerCompanies, condition=Q(company_id=company.id, player_id=user_id),
                                 condtion_create={'company_id': company.id, 'player_id': user_id,
                                                  'shares_amount': amount, 'preferred_shares_amount': 0,
                                                  'isFounder': False, 'isHead': False})
        else:
            raise CustomException(f'The current number of shares on the exchange is {stock_shares.amount}, you want {amount}')
    else:
        raise CustomException('You need more silver')

def buy_management_shares(user_id, ticker, amount, price, pk):
    """buys company shares in a certain quantity at a fixed price"""
    company = get_object(model=Company, condition=Q(ticker=ticker))
    stock_shares = get_object(model=SharesExchange, condition=Q(company=company, id=pk))
    buyer = get_object(model=Player, condition=Q(id=user_id))

    full_price = int(amount * price)

    if buyer.gold >= full_price:
        if stock_shares.amount >= amount:
            head_of_company = get_object(model=PlayerCompanies, condition=Q(company_id=company.id, isHead=True))

            if stock_shares.player.id == head_of_company.player.id: # if seller is head of the company then all funds will go to the company
                company.gold_reserve += full_price
                company.save(document=True)
            else: # otherwise funds will go to the seller
                stock_shares.player.gold += full_price
                stock_shares.player.save()

            buyer.gold -= full_price
            stock_shares.amount -= amount
            head_of_company.preffered_shares_amount -= amount

            if stock_shares.amount <= amount:
                stock_shares.delete()
            else:
                stock_shares.save()

            head_of_company.save(), buyer.save()

            get_object_or_create(PlayerCompanies, condition=Q(company_id=company.id, player_id=user_id),
                                 condtion_create={'company_id': company.id, 'player_id': user_id, 'shares_amount': 0,
                                                  'preferred_shares_amount': amount, 'isFounder': False, 'isHead': False})
        else:
            raise CustomException(f'The current number of shares on the exchange is {stock_shares.amount}, you need {amount}')
    else:
        raise CustomException('You need more gold')


def transfer_money_from_buying_shares(seller, shares_type, company, player, available_shares, total_cost_for_lot):
    """charging money to the seller or company"""
    seller.shares_amount -= available_shares
    seller.save()

    if seller.isHead:
        company.silver_reserve += total_cost_for_lot if shares_type == SharesTypes.ORDINARY else company.gold_reserve
    else:
        if shares_type == SharesTypes.ORDINARY:
            player.silver += total_cost_for_lot
            player.save()
        elif shares_type == SharesTypes.PREFERRED:
            player.gold += total_cost_for_lot
            player.save()


def buy_shares_wholesale(user_id, ticker, amount, offered_money, shares_type):
    """
    buys company shares in a certain quantity within a given price.
    offered_money is the money that the user is willing to give for a specific number of shares.
    shares will be purchased with available (transferred) money.
    money for the purchase will go to the company if the seller is the head of the company,
    otherwise the seller will receive the money
    """
    company = get_object(model=Company, condition=Q(ticker=ticker))
    user = get_object(model=Player, condition=Q(id=user_id))
    offered_money = Decimal(offered_money)

    if shares_type == 1: # ordinary
        shares_type = SharesTypes.ORDINARY
        user_money = user.silver
    elif shares_type == 2: # preffered
        shares_type = SharesTypes.PREFERRED
        user_money = user.gold
    else:
        raise CustomException('Error in buy_shares_wholesale due to incorrect sharesType')

    if user_id is None:
        current_time = timezone.now()
        stock_shares_lots = get_available_company_shares_for_everyone(ticker, current_time)
    else:
        if not PlayerCompanies.objects.filter(company__ticker=ticker, player_id=user_id, isHead=True).exists():
            current_time = timezone.now()
            stock_shares_lots = get_availabale_company_shares_for_shareholders(ticker, current_time, user_id)
        else:
            stock_shares_lots = get_available_company_shares_for_owners(ticker, user_id)

    if user_money >= offered_money:
        total_purchased = 0
        total_paid = Decimal('0.00')
        remaining_money = Decimal(offered_money)
        remaining_amount = Decimal(amount)

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
                player = lot.player

                seller = PlayerCompanies.objects.filter(company_id=lot.company_id, player_id=lot.player.id).first()
                if seller: # charging money to the seller or company
                    seller.shares_amount -= available_shares
                    seller.save()

                    if seller.isHead:
                        company.silver_reserve += total_cost_for_lot if shares_type == SharesTypes.ORDINARY else company.gold_reserve
                    else:
                        if shares_type == SharesTypes.ORDINARY:
                            player.silver += total_cost_for_lot
                            player.save()
                        elif shares_type == SharesTypes.PREFERRED:
                            player.gold += total_cost_for_lot
                            player.save()
                else:
                    raise CustomException('something happened wrong with seller in buy_shares_wholesale')
            else:
                max_affordable_shares = int(remaining_money // Decimal(lot.price))
                total_purchased += max_affordable_shares
                total_paid += Decimal(max_affordable_shares) * Decimal(lot.price)
                remaining_money -= Decimal(max_affordable_shares) * Decimal(lot.price)
                remaining_amount -= max_affordable_shares

                lot.amount -= max_affordable_shares
                lot.save()
                player = lot.player

                seller = PlayerCompanies.objects.filter(company_id=lot.company_id, player_id=lot.player.id).first()
                if seller: # charging money to the seller or company
                    seller.shares_amount -= available_shares
                    seller.save()

                    if seller.isHead:
                        company.silver_reserve += total_cost_for_lot if shares_type == SharesTypes.ORDINARY else company.gold_reserve
                    else:
                        if shares_type == SharesTypes.ORDINARY:
                            player.silver += total_cost_for_lot
                            player.save()
                        elif shares_type == SharesTypes.PREFERRED:
                            player.gold += total_cost_for_lot
                            player.save()
                else:
                    raise CustomException('something happened wrong with seller in buy_shares_wholesale')
                break
        else:
            raise CustomException("Not enough funds to buy any shares or no shares available.")

        if total_purchased == 0:
            raise CustomException("Not enough funds to buy any shares or no shares available.")

        transaction = SharesWholesaleTrade.objects.create(company=company, reserved_money=offered_money, paid=total_paid,
                                                          desired_quantity=amount, shares_type=shares_type, buyer=user,
                                                          purchased=total_purchased)
        # accrual of shares to users
        if shares_type == 1: # ordinary
            obj, is_created = get_object_or_create(model=PlayerCompanies, condition=Q(player_id=user_id, company=company),
                                                   condtion_create={'player_id': user_id, 'company': company,
                                                                    'isFounder': False, 'shares_amount': total_purchased,
                                                                    'isHead': False, 'preferred_shares_amount': 0})
            if not is_created:
                obj.shares_amount += total_purchased
                obj.save()

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
