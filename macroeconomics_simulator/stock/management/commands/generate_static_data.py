from django.core.management import BaseCommand

from stock.models import ProductType, CompanyType, AvailableProductsForProduction, CompanyRecipe, Recipe, \
    ProductsExchange, StateLaw
from stock.utils import CompanyTypes, ProductTypes


def add_available_products_for_production(company_instance):
    company_type = company_instance.type
    product_type = None
    if company_type in [CompanyTypes.FARM, CompanyTypes.FISH_FARM, CompanyTypes.PLANTATION, CompanyTypes.DEEP_SEA_FISHING_ENTERPRISE]:
        product_type = ProductTypes.UNPROCESSED_FOOD
    elif company_type == CompanyTypes.MINE:
        product_type = ProductTypes.MINERALS
    elif company_type == CompanyTypes.ORE_MINE:
        product_type = ProductTypes.BASE_METALS
    elif company_type == CompanyTypes.QUARRY:  # slate | limestone | clay - construction raw materials
        product_type = ProductTypes.CONSTRUCTION_RAW_MATERIALS
    elif company_type == CompanyTypes.SAWMILL:
        product_type = ProductTypes.WOOD
    elif company_type == CompanyTypes.FOOD_FACTORY:
        product_type = ProductTypes.PROCESSED_FOOD
    elif company_type == CompanyTypes.CHEMICAL_PLANT:
        product_type = ProductTypes.CHEMICALS
    elif company_type == CompanyTypes.METALLBURGICAL_PLANT:
        product_type = ProductTypes.PROCESSED_METALS
    elif company_type in [CompanyTypes.BRICK_FACTORY, CompanyTypes.GLASS_FACTORY, CompanyTypes.CONSTRUCTION_COMPANY]:
        product_type = ProductTypes.BUILDING_MATERIALS
    elif company_type == CompanyTypes.WOOD_PROCESSING_PLANT:
        product_type = ProductTypes.PROCESSED_WOOD
    elif company_type == CompanyTypes.TEXTILE_FACTORY:
        product_type = ProductTypes.TEXTILE
    elif company_type == CompanyTypes.PHARMACEUTICAL_COMPANY:
        product_type = ProductTypes.MEDICINES
    elif company_type == CompanyTypes.MICROELECTRONICS_PRODUCTION_PLANT:
        product_type = ProductTypes.MICROELECTRONICS
    elif company_type == CompanyTypes.ENGINEERING_PLANT:
        product_type = ProductTypes.MECHANICAL_PARTS
    elif company_type == CompanyTypes.FURNITURE_FACTORY:
        product_type = ProductTypes.FURNITURES
    elif company_type == CompanyTypes.CLOTHING_FACTORY:
        product_type = ProductTypes.CLOTHING
    elif company_type == CompanyTypes.OIL_COMPANY:
        product_type = ProductTypes.OIL
    elif company_type == CompanyTypes.CLOTHING_FACTORY_2:
        product_type = ProductTypes.SPECIAL_CLOTHING
    elif company_type == CompanyTypes.DEFENSE_INDUSTRY:
        product_type = ProductTypes.WEAPONS
    elif company_type == CompanyTypes.OIL_REFINING_COMPANY:
        product_type = ProductTypes.FUEL

    if product_type:
        product_instance = ProductType.objects.get(type=product_type)
        AvailableProductsForProduction.objects.create(company_type=company_instance, product_type=product_instance)


def create_recipe(company_instance, *ingredients_with_amounts):
    recipe = Recipe.objects.create(company_type=company_instance)

    for company_type, amount in ingredients_with_amounts:
        ingredient = CompanyType.objects.get(type=company_type)
        CompanyRecipe.objects.create(recipe=recipe, ingredient=ingredient, amount=amount)


# mb there is something wrong
def add_advanced_company_recipes(company_type):  # adds recipes for tickers whose tier is higher than the first
    """
    probably it would be better to use fixtures, but considering that the balance may change, I chose this method,
    and it looks stupid...
    """
    company_instance = CompanyType.objects.get(type=company_type).type

    if company_type == CompanyTypes.FOOD_FACTORY:
        recipe_1 = Recipe.objects.create(company_type=company_instance)
        ingredient_1 = CompanyType.objects.get(type=CompanyTypes.FARM)
        CompanyRecipe.objects.create(recipe=recipe_1, ingredient=ingredient_1, amount=2)

        recipe_2 = Recipe.objects.create(company_type=company_instance)
        ingredient_2 = CompanyType.objects.get(type=CompanyTypes.FISH_FARM)
        CompanyRecipe.objects.create(recipe=recipe_2, ingredient=ingredient_2, amount=2)

        recipe_3 = Recipe.objects.create(company_type=company_instance)
        CompanyRecipe.objects.create(recipe=recipe_3, ingredient=ingredient_1, amount=1)
        CompanyRecipe.objects.create(recipe=recipe_3, ingredient=ingredient_2, amount=1)
    elif company_type == CompanyTypes.DEEP_SEA_FISHING_ENTERPRISE:
        create_recipe(company_instance, (CompanyTypes.FISH_FARM, 2))
    elif company_type == CompanyTypes.CHEMICAL_PLANT:
        create_recipe(company_instance, (CompanyTypes.MINE, 2))
    elif company_type == CompanyTypes.METALLBURGICAL_PLANT:
        create_recipe(company_instance, (CompanyTypes.ORE_MINE, 2))
    elif company_type == CompanyTypes.BRICK_FACTORY:
        create_recipe(company_instance, (CompanyTypes.QUARRY, 2))
    elif company_type == CompanyTypes.GLASS_FACTORY:
        create_recipe(company_instance, (CompanyTypes.QUARRY, 2))
    elif company_type == CompanyTypes.CONSTRUCTION_COMPANY:
        create_recipe(company_instance, (CompanyTypes.BRICK_FACTORY, 1), (CompanyTypes.GLASS_FACTORY, 1),
                      (CompanyTypes.TEXTILE_FACTORY, 1))
    elif company_type == CompanyTypes.WOOD_PROCESSING_PLANT:
        create_recipe(company_instance, (CompanyTypes.SAWMILL, 2))
    elif company_type == CompanyTypes.TEXTILE_FACTORY:
        create_recipe(company_instance, (CompanyTypes.PLANTATION, 2))
    elif company_type == CompanyTypes.PHARMACEUTICAL_COMPANY:
        create_recipe(company_instance, (CompanyTypes.FOOD_FACTORY, 1), (CompanyTypes.CHEMICAL_PLANT, 1))
    elif company_type == CompanyTypes.MICROELECTRONICS_PRODUCTION_PLANT:
        create_recipe(company_instance, (CompanyTypes.METALLBURGICAL_PLANT, 1), (CompanyTypes.CHEMICAL_PLANT, 1))
    elif company_type == CompanyTypes.ENGINEERING_PLANT:
        create_recipe(company_instance, (CompanyTypes.METALLBURGICAL_PLANT, 2))
    elif company_type == CompanyTypes.FURNITURE_FACTORY:
        create_recipe(company_instance, (CompanyTypes.TEXTILE_FACTORY, 1), (CompanyTypes.WOOD_PROCESSING_PLANT, 1))
    elif company_type == CompanyTypes.CLOTHING_FACTORY:
        create_recipe(company_instance, (CompanyTypes.TEXTILE_FACTORY, 2))
    elif company_type == CompanyTypes.OIL_COMPANY:
        create_recipe(company_instance, (CompanyTypes.DEEP_SEA_FISHING_ENTERPRISE, 1), (CompanyTypes.MINE, 1),
                      (CompanyTypes.ORE_MINE, 1))
    elif company_type == CompanyTypes.CLOTHING_FACTORY_2:
        create_recipe(company_instance, (CompanyTypes.CLOTHING_FACTORY, 2))
    elif company_type == CompanyTypes.DEFENSE_INDUSTRY:
        create_recipe(company_instance, (CompanyTypes.MICROELECTRONICS_PRODUCTION_PLANT, 1),
                      (CompanyTypes.ENGINEERING_PLANT, 1))
    elif company_type == CompanyTypes.OIL_REFINING_COMPANY:
        create_recipe(company_instance, (CompanyTypes.OIL_COMPANY, 1), (CompanyTypes.CHEMICAL_PLANT, 1))


class Command(BaseCommand):
    help = "command to fill database with static data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('generating static data...'))
        laws = [
            {"title": "Law on Supporting Small Businesses During Gold Market Shortages", "description": "During severe market crises, when there is a shortage of gold on the exchange, developed tickers in the higher economic sectors may only purchase gold through a gold auction to protect small businesses and ensure a more equitable distribution of resources."},
            {"title": "Law on State Monopoly over Gold Mining and Transit", "description": "The exclusive right to mine and transport gold belongs to the state."},
            {"title": "Law on Progressive Tax for Idle Gold", "description": "Gold that remains unused for an extended period is subject to mandatory purchase by the state."},
            {"title": "Law on State Support for Shareholding Companies", "description": "The state commits to purchasing products from tickers, at a state-determined price, if it owns at least 10% of their shares."},
            {"title": "Law on supporting beginning investors", "description": "Those, and only those, whose savings are less than 100 gold can open a company once for free, while the rest will have to pay the full amount in order to expand their influence"},
        ]

        pt = ProductTypes
        product_types = [product_type.value for product_type in ProductTypes]

        products_tier_1 = [pt.UNPROCESSED_FOOD, pt.MINERALS, pt.BASE_METALS, pt.CONSTRUCTION_RAW_MATERIALS, pt.WOOD,
                           pt.SLATE, pt.LIMESTONE, pt.CLAY]
        products_tier_2 = [pt.PROCESSED_FOOD, pt.PROCESSED_WOOD, pt.CHEMICALS, pt.PROCESSED_METALS, pt.BUILDING_MATERIALS,
                           pt.TEXTILE]
        products_tier_3 = [pt.MEDICINES, pt.MICROELECTRONICS, pt.MECHANICAL_PARTS, pt.FURNITURES, pt.CLOTHING]
        products_tier_4 = [pt.OIL]
        products_tier_5 = [pt.SPECIAL_CLOTHING, pt.WEAPONS, pt.FUEL]

        company_types = [company_type.value for company_type in CompanyTypes]
        default_companies = [CompanyTypes.FARM, CompanyTypes.FISH_FARM, CompanyTypes.MINE, CompanyTypes.QUARRY,
                             CompanyTypes.SAWMILL, CompanyTypes.PLANTATION, CompanyTypes.ORE_MINE]
        advanced_companies = [company_type.value for company_type in CompanyTypes if company_type not in default_companies]

        for product_type in product_types: # adding product types
            base_price = None
            if product_type in products_tier_1:
                base_price = 1
            elif product_type in products_tier_2:
                base_price = 2
            elif product_type in products_tier_3:
                base_price = 4
            elif product_type in products_tier_4:
                base_price = 6
            elif product_type in products_tier_5:
                base_price = 8
            purchase_price = base_price * 100

            product = ProductType.objects.create(type=product_type, base_price=base_price)
            ProductsExchange.objects.create(product=product, sale_price=base_price, purchase_price=purchase_price)

        for company_type in company_types: # adding company types
            company = CompanyType.objects.create(type=company_type)
            add_available_products_for_production(company)

        for advanced_company_type in advanced_companies: # adding recipes for tickers with a tier > 1
            add_advanced_company_recipes(advanced_company_type)

        for law in laws:  # creating basic laws
            StateLaw.objects.create(title=law.get('title'), description=law.get('description'))

        self.stdout.write(self.style.SUCCESS('Static data generation has been completed'))
