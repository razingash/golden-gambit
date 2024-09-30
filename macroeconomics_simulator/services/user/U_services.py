from django.db.models import Q

from services.base import get_object
from stock.models import Player, PlayerCompanies


def get_player(user_id):
    condition = Q(id=user_id)
    fields = ['username', 'silver', 'gold', 'last_login', 'date_joined']
    player = get_object(model=Player, condition=condition, fields=fields)

    return player

def get_user_companies(user_id):
    fields = ['company__type__type', 'company__ticker', 'company__gold_reserve', 'company__share_price']
    company = PlayerCompanies.objects.select_related('company').filter(player_id=user_id).order_by('-id').only(*fields)

    return company
