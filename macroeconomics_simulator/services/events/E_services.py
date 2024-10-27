from stock.models import ProductsExchange, ProductType, GlobalEvent
from stock.utils.utils_models import ProductTypes


"""calibrate production capacity"""


def events_manager():
    """checks whether the event needs to be launched, if so, then there is a probability of launching"""


def events_operator():
    """chooses which event to launch"""


def event_crop_failure(event: GlobalEvent, pt: ProductTypes):
    """                 impact on products prices
    + unprocessed food, processed food
                        impact on companies' production capacity
    -- FARM, PLANTATION
    - FOOD_FACTORY
    """
    event_value = event.state.value
    new_product_prices = []
    products_on_stock = ProductsExchange.objects.select_related('product').filter(
        product__type__in=[pt.PROCESSED_FOOD, pt.PROCESSED_FOOD]
    )
    if event_value == 2: # beginning
        pass
    elif event_value == 3: # culmination
        pass
    elif event_value == 4: # consequences
        pass


def event_rich_harvest(event: GlobalEvent, pt: ProductTypes):
    """                 impact on product prices
    - unprocessed food, processed food
                        impact on companies' production capacity
    ++ FARM, PLANTATION
    + FOOD_FACTORY
    """


def event_earthquake(event: GlobalEvent, pt: ProductTypes):
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


def event_flood(event: GlobalEvent, pt: ProductTypes):
    """                 impact on product prices
    ++ unprocessed food, processed food
    + clothing,
    [from 'no changes' to --] random products except [unprocessed food, processed food, oil, weapons]
                        impact on companies' production capacity
    [from - to --] for SAWMILL, FARM, PLANTATION
    [from - to --] random companies except FISH_FARM, DEEP_SEA_FISHING_ENTERPRISE
    """


def event_extreme_heat(event: GlobalEvent, pt: ProductTypes):
    """                 impact on product prices
    ++ unprocessed food
    + processed food
                        impact on companies' production capacity
    -- FARM, PLANTATION
    - DEEP_SEA_FISHING_ENTERPRISE
    """


def event_drought(event: GlobalEvent, pt: ProductTypes):
    """                 impact on product prices
    ++ unprocessed food
    + processed food, wood
                        impact on companies' production capacity
    -- FARM, PLANTATION
    - SAWMILL
    """


def event_forest_fires(event: GlobalEvent, pt: ProductTypes):
    """                 impact on product prices
    ++ wood, processed wood
    +
                        impact on companies' production capacity
    -- SAWMILL
    [from - to --] WOOD_PROCESSING_PLANT
    - FURNITURE_FACTORY,
    """


def event_epidemic(event: GlobalEvent, pt: ProductTypes):
    """                 impact on product prices
    [from + to ++] medicines
    - fuel
                        impact on companies' production capacity
    + CHEMICAL_PLANT
    [from + to ++] PHARMACEUTICAL_COMPANY
    - OIL_COMPANY, OIL_REFINING_COMPANY
    [from 'no changes' to -] random companies except OIL_COMPANY, OIL_REFINING_COMPANY
    """


def event_pandemic_outbreak(event: GlobalEvent, pt: ProductTypes):
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


def event_workers_strikes(event: GlobalEvent, pt: ProductTypes):
    """                 impact on product prices
    [from - to --] for several products
                        impact on companies' production capacity
    [from - to --] for several companies
    """


def event_protests(event: GlobalEvent, pt: ProductTypes):
    """                 impact on product prices
     [from 'no changes' to +] for all products
                        impact on companies' production capacity
    --- for one or two companies
    [from 'no changes' to -] for all companies
    """


def event_civil_war(event: GlobalEvent, pt: ProductTypes):
    """                 impact on product prices
    [from + to ++] for all products
                        impact on companies' production capacity
    [from - to --] for all products
    """


def event_war(event: GlobalEvent, pt: ProductTypes):
    """                 impact on product prices
    ++++ weapons, medicines, construction raw materials
    +++ fuel, special clothing
    ++ oil
    [from + to ++] for all products except weapons, fuel, oil, special clothing
                        impact on companies' production capacity
    +++++ DEFENSE_INDUSTRY,
    ++++ PHARMACEUTICAL_COMPANY
    +++ CONSTRUCTION_COMPANY, CLOTHING_FACTORY_2, MICROELECTRONICS_PRODUCTION_PLANT
    ++ BRICK_FACTORY, ENGINEERING_PLANT
    + GLASS_FACTORY, FOOD_FACTORY
    [from - to ---] for all
    """
