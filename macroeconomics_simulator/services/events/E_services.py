import random

from django.db import transaction
from django.db.models import Q

from services.company.C_services import recalculate_all_companies_prices
from stock.models import ProductsExchange, GlobalEvent, EventImpactOnProduct, EventIpmactOnCompany, \
    CompanyType, AvailableProductsForProduction
from stock.utils.utils_models import ProductTypes, EventTypes, EventStates, CompanyTypes


def events_manager(): # calibrate?
    """checks whether the event needs to be launched, if so, then there is a probability of launching"""
    active_events = GlobalEvent.objects.filter(~Q(state=EventStates.INACTIVE))

    probability = 0.1 * (0.005 / 0.1) ** ((len(active_events) - 4) / 10)
    random_value = random.random()

    if random_value < probability:
        event_num = random.randint(1, 14)
        events_operator(event_num)

        recalculate_all_companies_prices()
    elif random_value < probability * 2: # probability of pushing an active event
        event_num = active_events[random.randint(0, len(active_events)-1)].type.value
        events_operator(event_num)

        recalculate_all_companies_prices()

def events_operator(event_num):
    """chooses which event to launch"""
    # new_product_price = old_price(basic) + tier * price_jump
    # price_jumps are higher at the beginning and stabilize towards the end of the event
    # These settings are approximate and don't need to be applied in this order

    event = GlobalEvent.objects.get(type=EventTypes(event_num))
    price_jumps = { # bg - beginning, cn - culmination, cs - consequences
        "bg+": (10, 25), "bg++": (15, 45), "bg+++": (35, 65), "bg++++": (55, 105),
        "bg-": (-10, -25), "bg--": (-15, -45), "bg---": (-35, -65), "bg----": (-55, -105),
        "cn+": (10, 20), "cn++": (15, 40), "cn+++": (35, 60), "cn++++": (55, 100),
        "cn-": (-10, -20), "cn--": (-15, -40), "cn---": (-35, -60), "cn----": (-55, -100),
        "cs+": (5, 15), "cs++": (10, 35), "cs+++": (30, 55), "cs++++": (50, 95),
        "cs-": (-5, -15), "cs--": (-10, -35), "cs---": (-30, -55), "cs----": (-50, -95),
    }
    productivity_jumps = {
        "bg+": (1, 4), "bg++": (2, 5), "bg+++": (3, 7), "bg++++": (6, 10),
        "bg-": (-1, -4), "bg--": (-2, -5), "bg---": (-3, -7), "bg----": (-6, -10),
        "cn+": (1, 3), "cn++": (2, 4), "cn+++": (3, 6), "cn++++": (4, 8),
        "cn-": (-1, -3), "cn--": (-2, -4), "cn---": (-3, -6), "cn----": (-4, -8),
        "cs+": (1, 2), "cs++": (2, 3), "cs+++": (3, 5), "cs++++": (4, 7),
        "cs-": (-1, -2), "cs--": (-2, -3), "cs---": (-3, -5), "cs----": (-4, -7),
    }
    if event_num == 1:
        event_crop_failure(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 2:
        event_rich_harvest(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 3:
        event_earthquake(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 4:
        event_flood(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 5:
        event_extreme_heat(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 6:
        event_drought(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 7:
        event_forest_fires(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 8:
        event_epidemic(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 9:
        event_pandemic_outbreak(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 10:
        event_workers_strikes(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 11:
        event_protests(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 12:
        event_civil_war(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)
    elif event_num == 13:
        event_war(event, price_jumps, productivity_jumps, pt=ProductTypes, ct=CompanyTypes)


def change_product_prices(items_for_update: dict, jumps):
    new_prices = {}
    for key, value in items_for_update:
        new_prices[key] = random.randint(*jumps.get(value))

    return new_prices


def clear_event_consequences(event: GlobalEvent) -> None:
    """neutralizes the consequences of the event"""
    affected_products = EventImpactOnProduct.objects.select_related('product').filter(event=event)
    affected_companies = EventIpmactOnCompany.objects.select_related('company_type').filter(event=event)
    products_to_update, company_types_to_update = [], []

    for affected_product in affected_products:
        influence = affected_product.influence # 'influence' stores the level of price change for sale only

        affected_product.product.purchase_price -= influence * 10
        affected_product.product.sale_price -= influence

        products_to_update.append(affected_product.product)

    for affected_company in affected_companies:
        influence = affected_company.influence # 'influence' stores the level of productivity

        affected_company.company_type.productivity -= influence
        company_types_to_update.append(affected_company.company_type)

    with transaction.atomic():
        ProductsExchange.objects.bulk_update(products_to_update, ['purchase_price', 'sale_price'])
        CompanyType.objects.bulk_update(company_types_to_update, ['productivity'])

        event.state = EventStates.INACTIVE
        event.save()

        affected_products.delete()
        affected_companies.delete()


def set_event_consequences(event: GlobalEvent, products_on_stock: list, new_products_prices: dict, new_productivity: dict) -> None:
    """changes the economy according to events"""
    changed_products = []
    changed_company_types = []
    for product_exchange in products_on_stock:
        product_type = product_exchange.product.type
        price_influence = new_products_prices.get(product_type)

        changed_product = EventImpactOnProduct(event=event, influence=price_influence, product=product_exchange)
        changed_products.append(changed_product)

    for key, value in new_productivity:
        changed_company_type = EventIpmactOnCompany(event=event, company__type=key, influence=value)
        changed_company_types.append(changed_company_type)

    with transaction.atomic():
        event.state += 1
        event.save()
        EventImpactOnProduct.objects.bulk_create(changed_products)


def event_crop_failure(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on products prices
    + unprocessed food, processed food
                        impact on companies' production capacity
    -- FARM, PLANTATION
    - FOOD_FACTORY
    """
    event_value = event.state.value
    if event_value == 4: # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=[pt.UNPROCESSED_FOOD, pt.PROCESSED_FOOD]
        )
        mod = get_modificator(event_value)

        products_for_update = {pt.UNPROCESSED_FOOD: f'{mod}+', pt.PROCESSED_FOOD: f'{mod}+'}
        companies_for_update = {ct.FARM: f'{mod}--', ct.PLANTATION: f'{mod}--', ct.FOOD_FACTORY: f'{mod}-'}

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_rich_harvest(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on product prices
    - unprocessed food, processed food
                        impact on companies' production capacity
    ++ FARM, PLANTATION
    + FOOD_FACTORY
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=[pt.UNPROCESSED_FOOD, pt.PROCESSED_FOOD]
        )
        mod = get_modificator(event_value)

        products_for_update = {pt.UNPROCESSED_FOOD: f'{mod}-', pt.PROCESSED_FOOD: f'{mod}-'}
        companies_for_update = {ct.FARM: f'{mod}++', ct.PLANTATION: f'{mod}++', ct.FOOD_FACTORY: f'{mod}+'}

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_earthquake(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on product prices
    ++ construction raw materials, furnitures, minerals, base metals
    + slate, limestone, clay, mechanical parts, processed food
                        impact on companies' production capacity
    [from + to +++] CONSTRUCTION_COMPANY
    --- MINE
    -- ORE_MINE
    [from - to --] DEEP_SEA_FISHING_ENTERPRISE
    [from - to ---] random companies except FISH_FARM, DEEP_SEA_FISHING_ENTERPRISE, MINE, ORE_MINE, CONSTRUCTION_COMPANY
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=[pt.CONSTRUCTION_RAW_MATERIALS, pt.FURNITURES, pt.MINERALS, pt.BASE_METALS, pt.SLATE,
                               pt.LIMESTONE, pt.CLAY, pt.MECHANICAL_PARTS, pt.PROCESSED_FOOD]
        )
        ct_fluctuation1 = random.randint(1, 3) * '+' # CONSTRUCTION_COMPANY
        ct_fluctuation2 = random.randint(1, 2) * '-' # DEEP_SEA_FISHING_ENTERPRISE
        companies_for_update = {}

        mod = get_modificator(event_value)

        products_for_update = {
            pt.CONSTRUCTION_RAW_MATERIALS: f'{mod}++', pt.FURNITURES: f'{mod}++', pt.MINERALS: f"{mod}++",
            pt.BASE_METALS: f"{mod}++", pt.SLATE: f"{mod}+", pt.LIMESTONE: f"{mod}+", pt.CLAY: f"{mod}+",
            pt.MECHANICAL_PARTS: f"{mod}+", pt.PROCESSED_FOOD: f"{mod}+"
        }

        for i in range(random.randint(1, 4)):
            fluctuation = random.randint(1, 3) * '-'
            companies_for_update[ct(random.randint(1, 25))] = f'{mod}{fluctuation}'

        companies_for_update.update({
            ct.CONSTRUCTION_COMPANY: f'{mod}{ct_fluctuation1}', ct.MINE: f'{mod}---',
            ct.ORE_MINE: f'{mod}--', ct.DEEP_SEA_FISHING_ENTERPRISE: f'{mod}{ct_fluctuation2}'
        })

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)

def event_flood(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on product prices
    ++ unprocessed food, processed food
    + clothing,
    [from 'no changes' to --] random products except [unprocessed food, processed food, oil, weapons]
                        impact on companies' production capacity
    [from - to --] for SAWMILL, FARM, PLANTATION
    [from - to --] random companies except FISH_FARM, DEEP_SEA_FISHING_ENTERPRISE, DEFENSE_INDUSTRY
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=[pt.UNPROCESSED_FOOD, pt.PROCESSED_FOOD, pt.CLOTHING]
        )
        mod = get_modificator(event_value)

        ct_fluctuation1 = random.randint(1, 2) * '-'
        ct_fluctuation2 = random.randint(1, 2) * '-'
        ct_fluctuation3 = random.randint(1, 2) * '-'

        products_for_update = {pt.UNPROCESSED_FOOD: f'{mod}++', pt.PROCESSED_FOOD: f'{mod}++', pt.CLOTHING: f'{mod}+'}
        companies_for_update = {}

        for i in range(random.randint(1, 6)):
            companies_for_update[ct(random.randint(1, 25))] = random.randint(1, 2) * '-'

        companies_for_update.update({
            ct.SAWMILL: ct_fluctuation1, ct.FARM: ct_fluctuation2, ct.PLANTATION: ct_fluctuation3
        })
        excluded_company_types = {ct.FISH_FARM, ct.DEEP_SEA_FISHING_ENTERPRISE, ct.DEFENSE_INDUSTRY}
        for key in excluded_company_types:
            companies_for_update.pop(key, None)

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_extreme_heat(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on product prices
    ++ unprocessed food
    + processed food
                        impact on companies' production capacity
    -- FARM, PLANTATION
    - DEEP_SEA_FISHING_ENTERPRISE
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=[pt.UNPROCESSED_FOOD, pt.PROCESSED_FOOD]
        )
        mod = get_modificator(event_value)

        products_for_update = {pt.UNPROCESSED_FOOD: f'{mod}++', pt.PROCESSED_FOOD: f'{mod}+'}
        companies_for_update = {ct.FARM: f'{mod}--', ct.PLANTATION: f'{mod}--', ct.DEEP_SEA_FISHING_ENTERPRISE: f'{mod}-'}

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_drought(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on product prices
    ++ unprocessed food
    + processed food, wood
                        impact on companies' production capacity
    -- FARM, PLANTATION
    - SAWMILL
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=[pt.UNPROCESSED_FOOD, pt.PROCESSED_FOOD, pt.WOOD]
        )
        mod = get_modificator(event_value)

        products_for_update = {pt.UNPROCESSED_FOOD: f'{mod}++', pt.PROCESSED_FOOD: f'{mod}++', pt.WOOD: f'{mod}+'}
        companies_for_update = {ct.FARM: f'{mod}--', ct.PLANTATION: f'{mod}--', ct.SAWMILL: f'{mod}-'}

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_forest_fires(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on product prices
    ++ wood, processed wood
    +
                        impact on companies' production capacity
    -- SAWMILL
    [from - to --] WOOD_PROCESSING_PLANT
    - FURNITURE_FACTORY,
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=[pt.WOOD, pt.PROCESSED_WOOD]
        )
        mod = get_modificator(event_value)
        ct_fluctuation1 = random.randint(1, 2) * '-'

        products_for_update = {pt.WOOD: f'{mod}++', pt.PROCESSED_WOOD: f'{mod}++'}
        companies_for_update = {ct.SAWMILL: f'{mod}--', ct.WOOD_PROCESSING_PLANT: ct_fluctuation1,
                                ct.FURNITURE_FACTORY: f'{mod}-'}

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_epidemic(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on product prices
    [from + to ++] medicines
    - fuel
                        impact on companies' production capacity
    + CHEMICAL_PLANT
    [from + to ++] PHARMACEUTICAL_COMPANY
    - OIL_COMPANY, OIL_REFINING_COMPANY
    [from 'no changes' to -] random companies except OIL_COMPANY, OIL_REFINING_COMPANY
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=[pt.MEDICINES, pt.FUEL]
        )
        mod = get_modificator(event_value)
        pt_fluctuation1 = random.randint(1, 2) * '+'
        ct_fluctuation1 = random.randint(1, 2) * '+'

        products_for_update = {pt.MEDICINES: f'{mod}{pt_fluctuation1}', pt.FUEL: f'{mod}-'}
        companies_for_update = {}

        for company_type in ct:
            fluctuation = random.randint(1, 2)
            if fluctuation == 1:
                companies_for_update[company_type] = f'{mod}-'

        companies_for_update.update({
            ct.CHEMICAL_PLANT: f'{mod}+', ct.PHARMACEUTICAL_COMPANY: ct_fluctuation1,
            ct.OIL_COMPANY: f'{mod}-', ct.OIL_REFINING_COMPANY: f'{mod}-'
        })

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_pandemic_outbreak(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on product prices
    ++ medicines
    [from + to ++] processed food, chemicals
    - oil, fuel
                        impact on companies' production capacity
    ++ PHARMACEUTICAL_COMPANY
    [from + to ++] CHEMICAL_PLANT
    [from - to --] for all except PHARMACEUTICAL_COMPANY, CHEMICAL_PLANT, DEEP_SEA_FISHING_ENTERPRISE, FARM, FISH_FARM,
    MINE, ORE_MINE, QUARRY, SAWMILL
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=[pt.MEDICINES, pt.PROCESSED_FOOD, pt.CHEMICALS, pt.OIL, pt.FUEL]
        )
        mod = get_modificator(event_value)
        pt_fluctuation1 = random.randint(1, 2) * '+'
        pt_fluctuation2 = random.randint(1, 2) * '+'
        ct_fluctuation1 = random.randint(1, 2) * '+'

        products_for_update = {pt.MEDICINES: f'{mod}++', pt.PROCESSED_FOOD: f'{mod}{pt_fluctuation1}',
                               pt.CHEMICALS: f'{mod}{pt_fluctuation2}', pt.OIL: f"{mod}-", pt.FUEL: f"{mod}-"}
        excluded_companies = {
            ct.PHARMACEUTICAL_COMPANY, ct.CHEMICAL_PLANT, ct.DEEP_SEA_FISHING_ENTERPRISE, ct.FISH_FARM,
            ct.FISH_FARM, ct.MINE, ct.ORE_MINE, ct.QUARRY, ct.SAWMILL
        }
        companies_for_update = {
            company: f"{random.randint(1, 2) * '-'}"
            for company in ct if company not in excluded_companies
        }

        companies_for_update.update({
            ct.PHARMACEUTICAL_COMPANY: f'{mod}++', ct.CHEMICAL_PLANT: f'{mod}{ct_fluctuation1}'}
        )

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_workers_strikes(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None: # чекнуть эту хуйню |x3
    """                 impact on product prices
    [from + to ++] for several products
                        impact on companies' production capacity
    [from - to --] for several companies
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        random_companies = []
        for i in range(random.randint(1, 6)):
            random_companies.append(ct(random.randint(1, 25)))
        random_companies = list(dict.fromkeys(random_companies))

        available_products = AvailableProductsForProduction.objects.select_related('company_type', 'product_type').filter(
            company_type__type__in=random_companies
        )

        random_products = [i.product_type.type for i in available_products]
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=random_products
        )

        mod = get_modificator(event_value)
        products_for_update = {
            product: f'{mod}{random.randint(1, 2) * "+"}'
            for product in random_products
        }
        companies_for_update = {key: f'{mod}{random.randint(1, 2) * "-"}' for key in random_companies}

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_protests(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None: # че-то тут намутил, переделать
    """                 impact on product prices
     [from 'no changes' to +] for all products
                        impact on companies' production capacity
    --- for one or two companies
    [from 'no changes' to -] for all companies
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        company_types_for_change, targeted_company_types = [], []
        for company_type in ct:
            if random.randint(1, 2) == 1:
                company_types_for_change.append(company_type)

        for i in range(random.randint(1, 2)):
            k = random.randint(1, len(company_types_for_change))
            targeted_company_types.append(company_types_for_change[k])
            company_types_for_change.pop(k)

        company_types = company_types_for_change + targeted_company_types
        available_products = AvailableProductsForProduction.objects.select_related('company_type', 'product_type').filter(
            company_type__type__in=company_types
        )

        products_for_change = [_.product_type.type for _ in available_products]
        products_on_stock = ProductsExchange.objects.select_related('product').filter(
            product__type__in=products_for_change
        )

        mod = get_modificator(event_value)
        products_for_update = {
            product: f'{mod}{random.randint(1, 2) * "+"}'
            for product in products_for_change
        }
        companies_for_update = {key: f'{mod}{random.randint(1, 2) * "-"}' for key in company_types_for_change}

        companies_for_update.update({
            key: f'{mod}---' for key in targeted_company_types
        })

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_civil_war(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on product prices
    [from + to ++] for all products
                        impact on companies' production capacity
    [from - to --] for all companies
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').all()
        mod = get_modificator(event_value)

        products_for_update = {
            product: f'{mod}{random.randint(1, 2) * "+"}'
            for product in pt
        }
        companies_for_update = {
            company: f'{mod}{random.randint(1, 2) * "-"}'
            for company in ct
        }

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def event_war(event: GlobalEvent, price_jumps, productivity_jumps, pt, ct) -> None:
    """                 impact on product prices
    ++++ weapons, medicines, construction raw materials
    +++ fuel, special clothing
    ++ oil
    [from + to ++] for all products except weapons, fuel, oil, special clothing
                        impact on companies' production capacity
    ++++ DEFENSE_INDUSTRY,
    ++++ PHARMACEUTICAL_COMPANY
    +++ CONSTRUCTION_COMPANY, CLOTHING_FACTORY_2, MICROELECTRONICS_PRODUCTION_PLANT
    ++ BRICK_FACTORY, ENGINEERING_PLANT
    + GLASS_FACTORY, FOOD_FACTORY
    [from - to ---] for all
    """
    event_value = event.state.value
    if event_value == 4:  # from consequences, to inactive state
        clear_event_consequences(event)
    else:
        products_on_stock = ProductsExchange.objects.select_related('product').all()

        mod = get_modificator(event_value)
        products_for_update = {
            product: f'{mod}{random.randint(1, 2) * "+"}'
            for product in pt
        }
        products_for_update.update({
            pt.WEAPONS: f'{mod}++++', pt.MEDICINES: f'{mod}++++', pt.SPECIAL_CLOTHING: f'{mod}+++',
            pt.CONSTRUCTION_RAW_MATERIALS: f'{mod}++++', pt.FUEL: f'{mod}+++', pt.OIL: f'{mod}++'
        })
        companies_for_update = {
            company: f'{mod}{random.randint(1, 3) * "-"}'
            for company in ct
        }
        companies_for_update.update({
            ct.DEFENSE_INDUSTRY: f'{mod}++++', ct.PHARMACEUTICAL_COMPANY: f'{mod}++++', ct.FOOD_FACTORY: f'{mod}+',
            ct.CONSTRUCTION_COMPANY: f'{mod}+++', ct.CLOTHING_FACTORY_2: f'{mod}+++', ct.ENGINEERING_PLANT: f'{mod}++',
            ct.MICROELECTRONICS_PRODUCTION_PLANT: f'{mod}+++', ct.BRICK_FACTORY: f'{mod}++', ct.GLASS_FACTORY: f'{mod}+'
        })

        new_products_prices = change_product_prices(items_for_update=products_for_update, jumps=price_jumps)
        new_productivity = change_product_prices(items_for_update=companies_for_update, jumps=productivity_jumps)
        set_event_consequences(event=event, products_on_stock=products_on_stock,
                               new_products_prices=new_products_prices, new_productivity=new_productivity)


def get_modificator(event_value: int) -> str:
    if event_value == 1:  # bg
        mod = 'bg'
    elif event_value == 2:  # cn
        mod = 'cn'
    else:  # event_value == 3: # cs
        mod = 'cs'
    return mod
