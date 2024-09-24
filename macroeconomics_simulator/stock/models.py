import json
import os
import time
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from macroeconomics_simulator import settings
from stock.services import calculate_share_price, calculate_company_price


# Create your models here.
class CompanyTypes(models.IntegerChoices):
    FARM = 1, 'farm' # 1x
    FISH_FARM = 2, 'fish farm'
    MINE = 3, 'mine'
    ORE_MINE = 4, 'ore mine'
    QUARRY = 5, 'quarry'
    SAWMILL = 6, 'sawmill'
    PLANTATION = 7, 'plantation'
    FOOD_FACTORY = 8, 'food factory' # x2
    DEEP_SEA_FISHING_ENTERPRISE = 9, 'deep sea fishing enterprise'
    CHEMICAL_PLANT = 10, 'chemical plant'
    METALLBURGICAL_PLANT = 11, 'metallburgical plant'
    BRICK_FACTORY = 12, 'brick factory'
    GLASS_FACTORY = 13, 'glass factory'
    WOOD_PROCESSING_PLANT = 14, 'wood processing plant'
    TEXTILE_FACTORY = 15, 'textile factory'
    PHARMACEUTICAL_COMPANY = 16, 'pharmaceutical company' # x4
    MICROELECTRONICS_PRODUCTION_PLANT = 17, 'microelectonics production plant'
    ENGINEERING_PLANT = 18, 'engineering plant'
    FURNITURE_FACTORY = 19, 'furniture factory'
    CLOTHING_FACTORY = 20, 'clothing factory'
    OIL_COMPANY = 21, 'oil company' # x6
    OIL_REFINING_COMPANY = 22, 'oil refining company' # 8x
    DEFENSE_INDUSTRY = 23, 'defense industry'
    CONSTRUCTION_COMPANY = 24, 'construction company'
    CLOTHING_FACTORY_2 = 25, 'clothing factory 2'


class ProductTypes(models.IntegerChoices):
    UNPROCESSED_FOOD = 1, 'unprocessed food' # 1x | 2x
    MINERALS = 2, 'minerals'
    BASE_METALS = 3, 'base metals'
    SLATE = 4, 'slate'
    LIMESTONE = 5, 'limestone'
    CLAY = 6, 'clay'
    WOOD = 7, 'wood'
    # 2x
    PROCESSED_FOOD = 8, 'processed food'
    CHEMICALS = 9, 'chemicals'
    PROCESSED_METALS = 10, 'processed metals'
    BUILDING_MATERIALS = 11, 'building materials' # x8
    PROCESSED_WOOD = 12, 'processed wood'
    TEXTILE = 13, 'textile'
    # 4x
    MEDICINES = 14, 'medicines'
    MICROELECTRONICS = 15, 'microelectronics'
    MECHANICAL_PARTS = 16, 'mechanical parts'
    FURNITURES = 17, 'furnitures'
    CLOTHING = 18, 'clothing'
    OIL = 19, 'oil' # x6
    # x8
    SPECIAL_CLOTHING = 20, 'special clothing'
    WEAPONS = 21, 'weapons'
    FUEL = 22, 'fuel'
    CONSTRUCTION_RAW_MATERIALS = 23, 'construction raw materials'


class SharesTypes(models.IntegerChoices):
    ORDINARY = 1, 'ordinary'
    PREFERRED = 2, 'preferred'


class EventTypes(models.IntegerChoices):
    CROP_FAILURE = 1, 'crop failure'
    RICH_HARVEST = 2, 'rich harvest'
    EARTHQUAKE = 3, 'earthquake'
    LANDSLIDES = 4, 'landslides'
    FLOOD = 5, 'flood'
    EPIDEMIC = 6, 'epidemic'
    PROTESTS = 7, 'Protests'
    WAR = 8, 'war'


class Player(AbstractUser):
    uuid = models.UUIDField(primary_key=False, default=uuid4, unique=True, editable=False, blank=False, null=False)
    silver = models.PositiveBigIntegerField(default=0, blank=False, null=False)
    gold = models.PositiveBigIntegerField(default=0, blank=False, null=False)


class ProductType(models.Model):
    type = models.CharField(default=ProductTypes.choices, max_length=2, blank=False, null=False)

    class Meta:
        db_table = 'dt_ProductType'


class CompanyType(models.Model):
    """all changes caused by laws and events are reflected on this model, and not on the Company model"""
    type = models.CharField(default=CompanyTypes.choices, max_length=2, blank=False, null=False)
    cartoonist = models.SmallIntegerField(blank=False, null=False)

    def clean(self):
        if self._state.adding:
            cartoonist_1 = [CompanyTypes.FARM, CompanyTypes.FISH_FARM, CompanyTypes.MINE, CompanyTypes.ORE_MINE,
                            CompanyTypes.QUARRY, CompanyTypes.SAWMILL, CompanyTypes.PLANTATION]
            cartoonist_2 = [CompanyTypes.FOOD_FACTORY, CompanyTypes.DEEP_SEA_FISHING_ENTERPRISE,
                            CompanyTypes.CHEMICAL_PLANT, CompanyTypes.METALLBURGICAL_PLANT, CompanyTypes.BRICK_FACTORY,
                            CompanyTypes.GLASS_FACTORY, CompanyTypes.WOOD_PROCESSING_PLANT, CompanyTypes.TEXTILE_FACTORY]
            cartoonist_4 = [CompanyTypes.PHARMACEUTICAL_COMPANY, CompanyTypes.MICROELECTRONICS_PRODUCTION_PLANT,
                            CompanyTypes.ENGINEERING_PLANT, CompanyTypes.FURNITURE_FACTORY, CompanyTypes.CLOTHING_FACTORY]
            cartoonist_6 = CompanyTypes.OIL_COMPANY
            cartoonist_8 = [CompanyTypes.OIL_REFINING_COMPANY, CompanyTypes.DEFENSE_INDUSTRY,
                            CompanyTypes.CONSTRUCTION_COMPANY, CompanyTypes.CLOTHING_FACTORY_2]
            if self.type in cartoonist_1:
                self.cartoonist = 1
            elif self.type in cartoonist_2:
                self.cartoonist = 2
            elif self.type in cartoonist_4:
                self.cartoonist = 4
            elif self.type == cartoonist_6:
                self.cartoonist = 6
            elif self.type in cartoonist_8:
                self.cartoonist = 8

            super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'dt_CompanyType'

@receiver(post_save, sender=CompanyType) # it had to come up somewhere... later move signals and selection classes to utils
def create_inventory(sender, instance, created, **kwargs):
    if created:
        product_type = None
        if instance.type in [CompanyTypes.FARM, CompanyTypes.FISH_FARM, CompanyTypes.PLANTATION, CompanyTypes.DEEP_SEA_FISHING_ENTERPRISE]:
            product_type = ProductTypes.UNPROCESSED_FOOD
        elif instance.type == CompanyTypes.MINE:
            product_type = ProductTypes.MINERALS
        elif instance.type == CompanyTypes.ORE_MINE:
            product_type = ProductTypes.BASE_METALS
        elif instance.type == CompanyTypes.QUARRY: # slate | limestone | clay - construction raw materials
            product_type = ProductTypes.CONSTRUCTION_RAW_MATERIALS
        elif instance.type == CompanyTypes.SAWMILL:
            product_type = ProductTypes.WOOD
        elif instance.type == CompanyTypes.FOOD_FACTORY:
            product_type = ProductTypes.PROCESSED_FOOD
        elif instance.type == CompanyTypes.CHEMICAL_PLANT:
            product_type = ProductTypes.CHEMICALS
        elif instance.type == CompanyTypes.METALLBURGICAL_PLANT:
            product_type = ProductTypes.PROCESSED_METALS
        elif instance.type in [CompanyTypes.BRICK_FACTORY, CompanyTypes.GLASS_FACTORY, CompanyTypes.CONSTRUCTION_COMPANY]:
            product_type = ProductTypes.BUILDING_MATERIALS
        elif instance.type == CompanyTypes.WOOD_PROCESSING_PLANT:
            product_type = ProductTypes.PROCESSED_WOOD
        elif instance.type == CompanyTypes.TEXTILE_FACTORY:
            product_type = ProductTypes.TEXTILE
        elif instance.type == CompanyTypes.PHARMACEUTICAL_COMPANY:
            product_type = ProductTypes.MEDICINES
        elif instance.type == CompanyTypes.MICROELECTRONICS_PRODUCTION_PLANT:
            product_type = ProductTypes.MICROELECTRONICS
        elif instance.type == CompanyTypes.ENGINEERING_PLANT:
            product_type = ProductTypes.MECHANICAL_PARTS
        elif instance.type == CompanyTypes.FURNITURE_FACTORY:
            product_type = ProductTypes.FURNITURES
        elif instance.type == CompanyTypes.CLOTHING_FACTORY:
            product_type = ProductTypes.CLOTHING
        elif instance.type == CompanyTypes.OIL_COMPANY:
            product_type = ProductTypes.OIL
        elif instance.type == CompanyTypes.CLOTHING_FACTORY_2:
            product_type = ProductTypes.SPECIAL_CLOTHING
        elif instance.type == CompanyTypes.DEFENSE_INDUSTRY:
            product_type = ProductTypes.WEAPONS
        elif instance.type == CompanyTypes.OIL_REFINING_COMPANY:
            product_type = ProductTypes.FUEL

        if product_type:
            AvailableProductsForProduction.objects.create(company_type=instance, product_type=product_type)


class AvailableProductsForProduction(models.Model):
    company_type = models.ForeignKey(CompanyType, on_delete=models.DO_NOTHING)
    product_type = models.ForeignKey(ProductType, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'dt_AvailableProductsForProduction'


class Recipe(models.Model):
    type = models.CharField(default=CompanyTypes.choices, max_length=2, blank=False, null=False)
    isAvailable = models.BooleanField(default=True, blank=False, null=False)


class CompanyRecipe(models.Model):
    company = models.ForeignKey(CompanyType, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        db_table = 'dt_CompanyRecipies'


class Company(models.Model): # mb add share price, but the load will be too high
    type = models.OneToOneField(CompanyType, on_delete=models.DO_NOTHING)
    ticker = models.CharField(max_length=8, validators=[MinLengthValidator(4)], blank=False, null=False)
    shares_amount = models.PositiveBigIntegerField(blank=False, null=False)
    preferred_shares_amount = models.PositiveSmallIntegerField(blank=False, null=False)
    shares_price = models.PositiveSmallIntegerField(blank=False, null=False)
    silver_reserve = models.PositiveBigIntegerField(default=1000, blank=False, null=False)
    gold_reserve = models.PositiveBigIntegerField(default=0, blank=False, null=False)
    company_price = models.IntegerField(blank=False, null=False)
    dividendes_percent = models.PositiveSmallIntegerField(blank=False, null=False)
    history = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'companies'), match='.*\.json$',
                                   blank=False, null=False)
    founding_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

@receiver(post_save, sender=Company)
def fill_json_template_for_company(sender, instance, created, **kwargs): # most likely will change in the future
    json_path = os.path.join(settings.MEDIA_ROOT, 'companies', f"{instance.ticker}.json")
    if created:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        json_schema = {
            "ticker": instance.ticker,
            "type": instance.type,
            "founding date": instance.founding_date,
            "contents": []
        }

        with open(json_path, 'w') as json_file:
            json.dump(json_schema, json_file, indent=2)

        instance.history = json_path
        #company_income is 0 because number of sold products = 0
        company_price = calculate_company_price(0, instance.type.cartoonist, instance.gold_reserve, instance.silver_reserve)
        instance.company_price = company_price
        instance.shares_price = calculate_share_price(company_price=company_price, shares_amount=instance.shares_amount)
        instance.save()
    else:
        with open(json_path, 'r') as json_file:
            json_data = json.load(json_file)

        json_data["contents"].append({
            "timestamp": int(time.time()),
            "company_price": instance.company_price,
            "silver_reserve": instance.silver_reserve,
            "gold_reserve": instance.gold_reserve
        })

        with open(json_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=2)


class CompanyWarehouse(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT) # custom scenario
    product = models.ForeignKey(ProductType, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(default=0, blank=False, null=False)


class CompanySharesForSale(models.Model): # add scenario for deleting company
    """this model is needed so that the company’s shareholders and the head himself have a chance to buy back
     the shares before they are put up for trading on SharesExchange model"""
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
    shares_type = models.CharField(choices=SharesTypes.choices, max_length=1, blank=False, null=False)
    shares_amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)], blank=False, null=False)
    shares_price = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], blank=False, null=False)

    class Meta:
        db_table = 'dt_CompanySharesForSale'


class PlayerCompanies(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT) # user can't be deleted
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING) # add a scenario for merging companies
    shares_amount = models.PositiveBigIntegerField(blank=False, null=False)
    preferred_shares_amount = models.PositiveBigIntegerField(blank=False, null=False)
    isFounder = models.BooleanField(blank=False, null=False)
    isHead = models.BooleanField(blank=False, null=False)

    class Meta:
        db_table = 'dt_PlayerCompanies'


class CompanyData(models.Model): # improve this to make it is possible to modify these indicators through events
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    production_speed = models.PositiveSmallIntegerField(blank=False, null=False)
    production_volume = models.PositiveSmallIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'dt_CompanyData'


class SharesExchange(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE) # custom scenario?
    shares_type = models.CharField(choices=SharesTypes.choices, max_length=1, blank=False, null=False)
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], blank=False, null=False)
    price = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], blank=False, null=False)

    class Meta:
        db_table = 'dt_SharesExchange'


# Unrelated models
class GoldSilverExchange(models.Model):
    base_price = models.PositiveSmallIntegerField(default=1000, unique=True, blank=False, null=False)
    current_price = models.PositiveSmallIntegerField(default=1000, blank=False, null=False)
    amount = models.PositiveSmallIntegerField(default=1_000_000_000, blank=False, null=False)
    history = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'gold_to_silver'), match='.*\.json$',
                                   blank=False, null=False)

    class Meta:
        db_table = 'dt_GoldSilverExchange'

@receiver(post_save, sender=GoldSilverExchange)
def fill_json_template_for_company(sender, instance, created, **kwargs):
    json_path = os.path.join(settings.MEDIA_ROOT, 'gold_silver_rate', f"{instance.id}.json")
    if created:  # calculate current price and add in history
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        json_schema = {
            "base price": instance.base_price,
            "amount": instance.amount,
            "contents": []
        }

        with open(json_path, 'w') as file:
            json.dump(json_schema, file, indent=2)

        instance.history = json_path
        instance.save()
    else:
        with open(json_path, 'r') as file:
            json_data = json.load(file)

        json_data["contents"].append({
            "timestamp": int(time.time()),
            "current price": instance.current_price
        })

        with open(json_path, 'w') as file:
            json.dump(json_data, file, indent=2)


class ProductsExchange(models.Model):
    product = models.CharField(choices=ProductTypes.choices, max_length=2, blank=False, null=False)
    price = models.PositiveIntegerField(validators=[MinValueValidator(10)], blank=False, null=False)
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], blank=False, null=False)

    class Meta:
        db_table = 'dt_ProductsExchange'


class StateLaws(models.Model):
    """laws are needed to provide minimal information about what can and cannot be done(but there will be an opportunity)"""
    description = models.TextField(max_length=1500, blank=False, null=False)
    since = models.DateField(auto_now_add=True, blank=False, null=False)
    to = models.DateField(blank=True, null=True)
    isActual = models.BooleanField(default=True, blank=False, null=False)

    class Meta:
        db_table = 'dt_StateLaws'


class Events(models.Model): # mb improve this model
    """events are needed mainly to stabilize the market and force some players to lose their companies"""
    type = models.CharField(choices=EventTypes.choices, max_length=2, blank=False, null=False)
    since = models.DateField(auto_now_add=True, blank=False, null=False)
    to = models.DateField(blank=True, null=True)
    isActual = models.BooleanField(default=True, blank=False, null=False)

