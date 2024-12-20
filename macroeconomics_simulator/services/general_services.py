from stock.models import PlayerCompanies, GlobalEvent


def recalculation_of_the_shareholders_influence(company_id) -> None:
    """recalculates the influence of shareholders to determine the current head of the company"""
    head = PlayerCompanies.objects.filter(company_id=company_id).order_by('-preferred_shares_amount').only('preferred_shares_amount', 'isHead').first()
    current_head = PlayerCompanies.objects.filter(company_id=company_id, isHead=True).only('isHead').first()
    if current_head != head:
        current_head.isHead = False
        head.isHead = True
        current_head.save(), head.save()


def get_current_events():
    events = GlobalEvent.objects.only('type', 'state', 'description').filter(state__in=[2, 3, 4])

    return events
