from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from stock.models import Player, Company, PlayerCompanies, StateLaw, GlobalEvent, CompanyWarehouse, GoldSilverExchange, \
    ProductsExchange, SharesExchange, CompanyRecipe, Recipe, CompanyType
from stock.utils import ProductTypes


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']

    @staticmethod
    def validate_password(value):
        validate_password(value)
        return value

    @staticmethod
    def validate_username(value):
        if len(value) < 5:
            raise ValidationError("Username must contain more than 4 characters")
        if not value.isalnum():
            raise ValidationError("Username must not contain special characters")
        return value

    def create(self, validated_data):
        player = Player.objects.create_user(username=validated_data['username'], password=validated_data['password'])
        return player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'silver', 'gold', 'date_joined']



class CompanySerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    cartoonist = serializers.IntegerField(source='type.cartoonist')

    class Meta:
        model = Company
        fields = ['type', 'cartoonist', 'ticker', 'name', 'shares_amount', 'preferred_shares_amount', 'share_price',
                  'silver_reserve', 'gold_reserve', 'company_price', 'dividendes_percent', 'founding_date']

    def get_type(self, obj):
        return obj.type.get_type_display()


class CompanyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name', 'dividendes_percent')

    def update(self, instance, validated_data):
        if 'name' in validated_data:
            instance.name = validated_data.get('name', instance.name)

        if 'dividendes_percent' in validated_data:
            self.update_dividendes_percent(instance, validated_data['dividendes_percent'])

        instance.save()
        return instance

    def update_dividendes_percent(self, instance, dividendes_percent):
        permissible_fluctuation = Decimal(3)
        if abs(dividendes_percent) <= permissible_fluctuation:
            dividendes = instance.dividendes_percent + dividendes_percent
            if dividendes_percent == 0:
                raise serializers.ValidationError(f"Too low fluctuation - {dividendes_percent}%")
            if dividendes >= 0:
                if dividendes <= 50:
                    instance.dividendes_percent += dividendes_percent
                else:
                    raise serializers.ValidationError("Dividend percentage cannot be greater than 50")
            else:
                raise serializers.ValidationError("Dividend percentage cannot be negative ")
        else:
            raise serializers.ValidationError(f"Too high fluctuation for dividends, maximum - {permissible_fluctuation}%")


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['type', 'ticker', 'name', 'shares_amount', 'preferred_shares_amount', 'dividendes_percent']


class CompanyPrintNewSharesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['ticker', 'shares_amount', 'preferred_shares_amount']


class SharesExchangeListSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source='company.ticker')
    name = serializers.CharField(source='company.name')

    class Meta:
        model = SharesExchange
        fields = ['ticker', 'name', 'shares_type', 'amount', 'price']


class SellSharesSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source='company.ticker', read_only=True)

    class Meta:
        model = SharesExchange
        fields = ['ticker', 'shares_type', 'amount', 'price']

class SharesExchangeSerializer(serializers.ModelSerializer): # used in 3 places!
    class Meta:
        model = SharesExchange
        fields = ['shares_type', 'amount', 'price']


class PlayerCompaniesSerializer(serializers.ModelSerializer):
    company_type_display = serializers.SerializerMethodField()
    cartoonist = serializers.IntegerField(source="company.type.cartoonist")
    name = serializers.CharField(source="company.name")
    ticker = serializers.CharField(source="company.ticker")
    dividendes_percent = serializers.CharField(source="company.dividendes_percent")


    class Meta:
        model = PlayerCompanies
        fields = ['company_type_display', 'name', 'cartoonist', 'ticker', 'shares_amount', 'preferred_shares_amount',
                  'dividendes_percent', 'isFounder', 'isHead']

    def get_company_type_display(self, obj):
        return obj.company.type.get_type_display()


class WarehouseSerializer(serializers.ModelSerializer):
    product_type_display = serializers.SerializerMethodField()
    ticker = serializers.CharField(source='company.ticker', read_only=True)

    class Meta:
        model = CompanyWarehouse
        fields = ['ticker', 'amount', 'product_type_display']

    def get_product_type_display(self, obj):
        return obj.product.get_type_display()


class GoldSilverRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldSilverExchange
        fields = ['base_price', 'current_price', 'amount']


class GoldAmountSerializer(serializers.Serializer):
    amount = serializers.IntegerField()


class ProductsSerializer(serializers.ModelSerializer):
    product_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ProductsExchange
        fields = ['product_type_display', 'purchase_price', 'sale_price']

    def get_product_type_display(self, obj):
        return obj.product.get_type_display()


class ProductsTradingSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    company_ticker = serializers.CharField(max_length=8, min_length=4)
    product_type = serializers.ChoiceField(choices=ProductTypes.choices)

    def validate_company_ticker(self, value):
        if not Company.objects.filter(ticker=value).exists():
            raise serializers.ValidationError(f"Company with ticker {value} does not exist")
        return value


class LawsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateLaw
        fields = ['title', 'description', 'since', 'to', 'isActual']


class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalEvent
        fields = '__all__'


class TopPlayerSerializer(serializers.ModelSerializer): # could be useless later
    wealth = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Player
        fields = ['username', 'silver', 'gold', 'wealth']



class IngredientSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()

    class Meta:
        model = CompanyRecipe
        fields = ['type', 'type_display', 'amount']

    def get_type(self, obj):
        return obj.ingredient.type

    def get_type_display(self, obj):
        return obj.ingredient.get_type_display()


class CompanyRecipesSerializer(serializers.ModelSerializer):
    company_type = serializers.IntegerField(source="recipe.company_type")
    type_display = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = CompanyRecipe
        fields = ['company_type', 'type_display', 'ingredients']

    def get_type_display(self, obj):
        return obj.recipe.get_company_type_display()

    def get_ingredients(self, obj):
        company_recipes = CompanyRecipe.objects.filter(recipe=obj.recipe)
        return IngredientSerializer(company_recipes, many=True).data
