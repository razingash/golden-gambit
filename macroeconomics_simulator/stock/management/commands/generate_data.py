from django.core.management import BaseCommand

from stock.models import Player, ProductType, CompanyType, AvailableProductsForProduction, CompanyRecipe, Recipe
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
def add_advanced_company_recipes(company_type):  # adds recipes for companies whose tier is higher than the first
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
    help = "command for filling database"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('generating data...'))
        users = []
        company_types = [company_type.value for company_type in CompanyTypes]
        product_types = [product_type.value for product_type in ProductTypes]
        default_companies = [CompanyTypes.FARM, CompanyTypes.FISH_FARM, CompanyTypes.MINE, CompanyTypes.FOOD_FACTORY,
                             CompanyTypes.QUARRY, CompanyTypes.SAWMILL, CompanyTypes.PLANTATION, CompanyTypes.ORE_MINE]
        advanced_companies = [company_type.value for company_type in CompanyTypes if company_type not in default_companies]

        for product_type in product_types: # adding product types
            ProductType.objects.create(type=product_type)

        for company_type in company_types: # adding company types
            company = CompanyType.objects.create(type=company_type)
            add_available_products_for_production(company)

        for advanced_company_type in advanced_companies: # adding recipes for companies with a tier > 1
            add_advanced_company_recipes(advanced_company_type)

        for i in range(1, 11): # creating users
            user = Player.objects.create_user(username=f'djangobot{i}', password=f'djangobot{i}')
            users.append(user)
