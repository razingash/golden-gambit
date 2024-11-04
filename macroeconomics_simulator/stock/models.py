import json
import os
import time
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum, F

from macroeconomics_simulator import settings
from stock.utils.utils_models import ProductTypes, CompanyTypes, SharesTypes, EventTypes, \
    right_of_purchase_for_shareholders, right_of_purchase_for_owners, EventStates


def recalculate_company_price(company_instance): # good
    """company_cartoonist not included but most likely it is better to ignore it here"""
    company_silver = company_instance.silver_reserve

    warehouses = CompanyWarehouse.objects.filter(company_id=company_instance.pk).annotate(
        sale_price=F('product__productsexchange__sale_price')).aggregate(
        company_income=Sum(F('amount') * F('sale_price'))
    )
    company_income = warehouses['company_income'] if warehouses['company_income'] is not None else 0

    if company_instance.gold_reserve > 0:
        current_price = GoldSilverExchange.objects.only('current_price').first().current_price
        gold_price = current_price * company_instance.gold_reserve
        assets_price = gold_price + company_silver
    else:
        assets_price = company_silver

    shares_amount = Decimal(company_instance.shares_amount)
    share_price = Decimal(company_instance.share_price)
    dividendes_percent = Decimal(company_instance.dividendes_percent)

    productivity_factor = Decimal(2 * company_instance.type.productivity / 40) # additional sql query((
    commitment = shares_amount * share_price * dividendes_percent / 100

    company_price = round((assets_price + company_income - commitment) * productivity_factor, 2)

    return company_price


class Player(AbstractUser):
    uuid = models.UUIDField(primary_key=False, default=uuid4, unique=True, editable=False, blank=False, null=False)
    silver = models.DecimalField(default=30_000, validators=[MinValueValidator(Decimal(0))], max_digits=10, decimal_places=2,
                                 blank=False, null=False)
    gold = models.PositiveBigIntegerField(default=0, blank=False, null=False)

    class Meta:
        db_table = 'dt_Player'


class ProductType(models.Model):
    type = models.PositiveSmallIntegerField(choices=ProductTypes.choices, blank=False, null=False)
    base_price = models.PositiveSmallIntegerField(blank=False, null=False)

    def __str__(self):
        return ProductTypes(self.type).label

    class Meta:
        db_table = 'dt_ProductType'


class CompanyType(models.Model): # normally is 420 per hour, minimum is 4 p/h, maximum 840
    """ all changes caused by laws and events are reflected on this model, and not on the Company model
        if you need to change the default value for productivity, you must also change the 'base_productivity' variable
        in the 'set_event_consequences' and 'roll_back_event_consequences' functions
    """
    type = models.PositiveSmallIntegerField(choices=CompanyTypes.choices, blank=False, null=False)
    productivity = models.PositiveSmallIntegerField(default=20, validators=[MaxValueValidator(40)], blank=False,  null=False)
    cartoonist = models.PositiveSmallIntegerField(blank=False, null=False)
    external_influence = models.SmallIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return CompanyTypes(self.type).label

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
    company_type = models.PositiveSmallIntegerField(choices=CompanyTypes.choices, blank=False, null=False)
    isAvailable = models.BooleanField(default=True, blank=False, null=False)

    def __str__(self):
        return CompanyTypes(self.company_type).label

    class Meta:
        db_table = 'dt_Recipe'


class CompanyRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(CompanyType, on_delete=models.CASCADE) # ingredient?
    amount = models.PositiveSmallIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'dt_CompanyRecipies'


class Company(models.Model):
    type = models.ForeignKey(CompanyType, on_delete=models.DO_NOTHING)
    ticker = models.CharField(max_length=8, validators=[MinLengthValidator(4)], blank=False, null=False, unique=True)
    name = models.CharField(max_length=120, validators=[MinLengthValidator(6)], blank=False, null=False, unique=True)
    shares_amount = models.PositiveBigIntegerField(blank=False, null=False)
    preferred_shares_amount = models.PositiveSmallIntegerField(blank=False, null=False)
    share_price = models.DecimalField(validators=[MinValueValidator(Decimal(0))], max_digits=10, decimal_places=2,
                                      default=0, blank=False, null=False)
    silver_reserve = models.DecimalField(default=10000, validators=[MinValueValidator(Decimal(0))], max_digits=10,
                                         decimal_places=2, blank=False, null=False)
    gold_reserve = models.PositiveBigIntegerField(default=0, blank=False, null=False)
    company_price = models.IntegerField(blank=False, null=False)
    daily_company_price = models.IntegerField(blank=False, null=False)
    dividendes_percent = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    dividendes_change_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    history = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'tickers'), match='.*\.json$',
                                   blank=False, null=False)
    founding_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def save(self, *args, **kwargs):
        document = kwargs.pop('document', False)
        if not self.pk:
            date = datetime.now()
            year, month, day = date.year, date.month, date.day
            json_path = os.path.join(settings.MEDIA_ROOT, 'tickers', str(year), str(month), str(day), f"{self.ticker}.json")
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

            self.company_price = self.silver_reserve
            self.daily_company_price = self.company_price
            self.share_price = round(Decimal(self.silver_reserve) / Decimal(self.shares_amount), 2)

            document = True
        if document: # if document is True then the data will be written to json
            company_price = recalculate_company_price(self)
            self.company_price = company_price

            with open(self.history, 'r') as json_file:
                json_data = json.load(json_file)

            json_data["contents"].append({
                "timestamp": int(time.time()),
                "company_price": float(company_price),
                "silver_reserve": float(self.silver_reserve),
                "gold_reserve": float(self.gold_reserve)
            })

            with open(self.history, 'w') as json_file:
                json.dump(json_data, json_file, indent=2)

        super(Company, self).save(*args, **kwargs)

    class Meta:
        db_table = 'dt_Company'


class CompanyWarehouse(models.Model):
    """50_000 thousand for the company's target product and 10_000 for other products"""
    company = models.ForeignKey(Company, on_delete=models.PROTECT) # custom scenario
    product = models.ForeignKey(ProductType, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(default=0, blank=False, null=False)
    remainder = models.PositiveIntegerField(default=0, blank=True, null=True)
    max_amount = models.PositiveIntegerField(default=10000, blank=False, null=False)
    check_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        db_table = 'dt_CompanyWarehouse'


class PlayerCompanies(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT) # user can't be deleted
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING) # add a scenario for merging tickers
    shares_amount = models.PositiveBigIntegerField(blank=False, null=False)
    preferred_shares_amount = models.PositiveBigIntegerField(blank=False, null=False)
    isFounder = models.BooleanField(default=True, blank=False, null=False)
    isHead = models.BooleanField(default=True, blank=False, null=False)

    class Meta:
        db_table = 'dt_PlayerCompanies'


class SharesExchange(models.Model):
    """this model is needed so that the company’s shareholders and the head himself have a chance to buy back
        the shares before they are put up for trading on SharesExchange model"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE) # custom scenario?
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    shares_type = models.PositiveSmallIntegerField(choices=SharesTypes.choices, blank=False, null=False)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100_000)], blank=False, null=False)
    price = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100_00)], blank=False, null=False)
    owners_right = models.DateTimeField(default=right_of_purchase_for_owners, blank=True, null=True)
    shareholders_right = models.DateTimeField(default=right_of_purchase_for_shareholders, blank=True, null=True)

    class Meta:
        db_table = 'dt_SharesExchange'


class SharesWholesaleTrade(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    buyer = models.ForeignKey(Player, on_delete=models.CASCADE)
    shares_type = models.PositiveSmallIntegerField(choices=SharesTypes.choices, blank=False, null=False)
    desired_quantity = models.PositiveSmallIntegerField(blank=False, null=False, validators=[MinValueValidator(1)])
    reserved_money = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], blank=False, null=False)
    purchased = models.PositiveSmallIntegerField(blank=False, null=False, validators=[MinValueValidator(1)]) # how many shares were purchased
    paid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
                               blank=False, null=False) # how much was paid

    class Meta:
        db_table = 'dt_SharesWholesaleTrade'


class GoldSilverExchange(models.Model):
    base_price = models.PositiveSmallIntegerField(default=1000, unique=True, blank=False, null=False)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=1000, blank=False, null=False)
    amount = models.PositiveIntegerField(default=1_000_000_000, blank=False, null=False)
    history = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'gold_to_silver'), match='.*\.json$',
                                   blank=False, null=False)

    def to_dict(self):
        return {
            'current_price': str(self.current_price),
            'amount': str(self.amount)
        }

    class Meta:
        db_table = 'dt_GoldSilverExchange'


class ProductsExchange(models.Model):
    """changes caused by laws and events can be reflected in fields"""
    product = models.OneToOneField(ProductType, on_delete=models.CASCADE)
    purchase_price = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=False, null=False)
    sale_price = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=False, null=False)
    external_influence = models.SmallIntegerField(default=0, blank=False, null=False)

    class Meta:
        db_table = 'dt_ProductsExchange'


class StateLaw(models.Model):
    """laws are needed to provide minimal information about what can and cannot be done(but there will be an opportunity)"""
    title = models.CharField(max_length=300, blank=False, null=False)
    description = models.TextField(max_length=1500, blank=False, null=False)
    since = models.DateField(auto_now_add=True, blank=False, null=False)
    to = models.DateField(blank=True, null=True)
    isActual = models.BooleanField(default=True, blank=False, null=False)

    class Meta:
        db_table = 'dt_StateLaws'


class GlobalEvent(models.Model): # mb improve this model (add fields for custom description)
    """
    events are needed mainly to stabilize the market and force some players to lose their companies.
    you can make a separate table for interrelated descriptions of events, but even if the maximum number of events
    is only 5 events, you will have to do 13! / 8! special cases
    """
    type = models.PositiveSmallIntegerField(choices=EventTypes.choices, blank=False, null=False)
    state = models.PositiveSmallIntegerField(choices=EventStates.choices, default=EventStates.INACTIVE, blank=False, null=False)
    description = models.CharField(blank=False, null=False, max_length=500)
    active_since = models.DateTimeField(blank=False, null=True, auto_now=True)

    class Meta:
        db_table = 'dt_Events'


class EventImpactOnProduct(models.Model):
    """needed to track random price changes so that after a change in the state of events, prices can be changed correctly"""
    event = models.ForeignKey(GlobalEvent, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(ProductsExchange, on_delete=models.DO_NOTHING)
    influence = models.SmallIntegerField(blank=False, null=False) # size of the price jump FOR SALE

    class Meta:
        db_table = 'dt_Impact_on_Products'


class EventIpmactOnCompany(models.Model):
    """needed to track random price changes so that after a change in the state of events, prices can be changed correctly"""
    event = models.ForeignKey(GlobalEvent, on_delete=models.DO_NOTHING)
    company_type = models.ForeignKey(CompanyType, on_delete=models.DO_NOTHING)
    influence = models.SmallIntegerField(blank=False, null=False) # this field contains the level of productivity change

    class Meta:
        db_table = 'dt_Impact_on_Companies'
