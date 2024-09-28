import json
import os
import time
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models

from macroeconomics_simulator import settings
from stock.utils import ProductTypes, CompanyTypes, SharesTypes, EventTypes


class Player(AbstractUser):
    uuid = models.UUIDField(primary_key=False, default=uuid4, unique=True, editable=False, blank=False, null=False)
    silver = models.DecimalField(default=0, validators=[MinValueValidator(Decimal(0))], max_digits=10, decimal_places=2,
                                 blank=False, null=False)
    gold = models.PositiveBigIntegerField(default=0, blank=False, null=False)

    class Meta:
        db_table = 'dt_Player'


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


class AvailableProductsForProduction(models.Model):
    company_type = models.ForeignKey(CompanyType, on_delete=models.DO_NOTHING)
    product_type = models.ForeignKey(ProductType, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'dt_AvailableProductsForProduction'


class Recipe(models.Model):
    company_type = models.CharField(default=CompanyTypes.choices, max_length=2, blank=False, null=False)
    isAvailable = models.BooleanField(default=True, blank=False, null=False)

    class Meta:
        db_table = 'dt_Recipe'


class CompanyRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(CompanyType, on_delete=models.CASCADE) # ingredient?
    amount = models.PositiveSmallIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'dt_CompanyRecipies'


class Company(models.Model): # mb add share price, but the load will be too high
    type = models.ForeignKey(CompanyType, on_delete=models.DO_NOTHING)
    ticker = models.CharField(max_length=8, validators=[MinLengthValidator(4)], blank=False, null=False, unique=True)
    name = models.CharField(max_length=120, validators=[MinLengthValidator(6)], blank=False, null=False, unique=True)
    shares_amount = models.PositiveBigIntegerField(blank=False, null=False)
    preferred_shares_amount = models.PositiveSmallIntegerField(blank=False, null=False)
    share_price = models.PositiveBigIntegerField(blank=False, null=False)
    silver_reserve = models.DecimalField(default=1000, validators=[MinValueValidator(Decimal(0))], max_digits=10,
                                         decimal_places=2, blank=False, null=False)
    gold_reserve = models.PositiveBigIntegerField(default=0, blank=False, null=False)
    company_price = models.IntegerField(blank=False, null=False)
    dividendes_percent = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    history = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'companies'), match='.*\.json$',
                                   blank=False, null=False)
    founding_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def save(self, *args, **kwargs): # учесть золото
        json_path = os.path.join(settings.MEDIA_ROOT, 'companies', f"{self.ticker}.json")
        if not self.pk:
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            json_schema = {
                "ticker": self.ticker,
                "company_type": self.type_id,
                "founding date": int(time.time()),
                "contents": []
            }

            with open(json_path, 'w') as json_file:
                json.dump(json_schema, json_file, indent=2)

            self.history = json_path
            share_price = int(self.silver_reserve / (3 * self.shares_amount))
            commitment = int(self.shares_amount * share_price * self.dividendes_percent / 100)

            company_price = (self.silver_reserve + 0 * self.type.cartoonist) - commitment

            self.company_price = company_price
            self.share_price = int(company_price / self.shares_amount)

        else: # don't change
            with open(json_path, 'r') as json_file:
                json_data = json.load(json_file)
            json_data["contents"].append({
                "timestamp": int(time.time()),
                "company_price": self.company_price,
                "silver_reserve": float(round(self.silver_reserve, 2)),
                "gold_reserve": self.gold_reserve
            })

            with open(json_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=2)

        super(Company, self).save(*args, **kwargs)

    class Meta:
        db_table = 'dt_Company'


class CompanyWarehouse(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT) # custom scenario
    product = models.ForeignKey(ProductType, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        db_table = 'dt_CompanyWarehouse'


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
    isFounder = models.BooleanField(default=True, blank=False, null=False)
    isHead = models.BooleanField(default=True, blank=False, null=False)

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


class ProductsExchange(models.Model):
    product = models.CharField(choices=ProductTypes.choices, max_length=2, blank=False, null=False)
    price = models.PositiveIntegerField(validators=[MinValueValidator(10)], blank=False, null=False)
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], blank=False, null=False)

    class Meta:
        db_table = 'dt_ProductsExchange'


class StateLaw(models.Model):
    """laws are needed to provide minimal information about what can and cannot be done(but there will be an opportunity)"""
    description = models.TextField(max_length=1500, blank=False, null=False)
    since = models.DateField(auto_now_add=True, blank=False, null=False)
    to = models.DateField(blank=True, null=True)
    isActual = models.BooleanField(default=True, blank=False, null=False)

    class Meta:
        db_table = 'dt_StateLaws'


class GlobalEvent(models.Model): # mb improve this model | find another name
    """events are needed mainly to stabilize the market and force some players to lose their companies"""
    type = models.CharField(choices=EventTypes.choices, max_length=2, blank=False, null=False)
    since = models.DateField(auto_now_add=True, blank=False, null=False)
    to = models.DateField(blank=True, null=True)
    isActual = models.BooleanField(default=True, blank=False, null=False)

    class Meta:
        db_table = 'dt_Events'

