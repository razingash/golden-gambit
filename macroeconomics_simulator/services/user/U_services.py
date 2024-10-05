from django.core.paginator import Paginator
from django.db.models import Q, F, Value

from services.base import get_object, paginate_objects
from stock.models import Player, PlayerCompanies, GoldSilverExchange


def get_player(user_id):
    condition = Q(id=user_id)
    fields = ['username', 'silver', 'gold', 'last_login', 'date_joined']
    player = get_object(model=Player, condition=condition, fields=fields)

    return player


def get_user_companies(user_id, query_params):
    fields = ['company__type__type', 'company__ticker', 'company__gold_reserve', 'company__share_price']
    companies = PlayerCompanies.objects.select_related('company').filter(player_id=user_id, isHead=True).order_by('-id').only(*fields)

    obj, has_next = paginate_objects(companies, query_params)
    return obj, has_next

def get_user_shares(user_id, query_params):
    fields = ['company__type__type', 'company__ticker', 'company__gold_reserve', 'company__share_price']
    shares = PlayerCompanies.objects.select_related('company').filter(player_id=user_id).order_by('-id').only(*fields)

    obj, has_next = paginate_objects(shares, query_params)
    return obj, has_next

def get_top_users(amount=10):
    current_gold_price = GoldSilverExchange.objects.only('current_price').first().current_price

    users = Player.objects.annotate(
        converted_gold=F('gold') * Value(current_gold_price), wealth=F('silver') + F('converted_gold')
    ).order_by('-wealth')[:amount]

    return users
