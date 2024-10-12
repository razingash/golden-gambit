from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from stock.models import Player, Company, PlayerCompanies, StateLaw, GlobalEvent, CompanyWarehouse, GoldSilverExchange, \
    ProductsExchange, SharesExchange, CompanyRecipe, SharesWholesaleTrade
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


class DividedCompanySerializer(serializers.ModelSerializer):
    """separates information for ordinary users and the head of the company"""
    type = serializers.SerializerMethodField()
    cartoonist = serializers.IntegerField(source='type.cartoonist')
    isHead = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['type', 'cartoonist', 'ticker', 'name', 'shares_amount', 'preferred_shares_amount', 'share_price',
                  'silver_reserve', 'gold_reserve', 'company_price', 'dividendes_percent', 'founding_date', 'isHead']

    def get_isHead(self, obj):
        user = self.context['user']
        if user.is_authenticated:
            player_company = PlayerCompanies.objects.filter(company=obj, player=user, isHead=True).first()
            return player_company is not None
        else:
            return False

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
        current_dividendes = instance.dividendes_percent

        if dividendes_percent <= 0:
            raise serializers.ValidationError({'dividendes_percent': f"Too low fluctuation - {dividendes_percent}%"})

        fluctuation = dividendes_percent - current_dividendes

        if abs(fluctuation) > permissible_fluctuation:
            raise serializers.ValidationError(
                {'dividendes_percent': f"Too high fluctuation for dividends, maximum - {permissible_fluctuation}%"})

        if dividendes_percent <= 50:
            instance.dividendes_percent = dividendes_percent
        else:
            raise serializers.ValidationError({'dividendes_percent': "Dividend percentage cannot be greater than 50"})



class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['type', 'ticker', 'name', 'shares_amount', 'preferred_shares_amount', 'dividendes_percent']

    def validate_shares_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero, clown")
        return value

    def validate_preferred_shares_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero, clown")
        return value

    def validate_dividendes_percent(self, value):
        if value <= 2:
            raise serializers.ValidationError("Dividendes percent must be greater or equal 2")
        return value


class CompanyPrintNewSharesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['ticker', 'shares_amount', 'preferred_shares_amount']


class SharesExchangeWholesaleListSerializer(serializers.Serializer):
    ticker = serializers.CharField(source='company__ticker')
    name = serializers.CharField(source='company__name')
    shares_type = serializers.IntegerField()
    total_amount = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='min_price')


class SharesExchangeListSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source='company.ticker')
    name = serializers.CharField(source='company.name')

    class Meta:
        model = SharesExchange
        fields = ['id', 'ticker', 'name', 'shares_type', 'amount', 'price']


class SellSharesSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source='company.ticker', read_only=True)

    class Meta:
        model = SharesExchange
        fields = ['ticker', 'shares_type', 'amount', 'price']

class SharesExchangeSerializer(serializers.ModelSerializer): # used in 3 places!
    class Meta:
        model = SharesExchange
        fields = ['id', 'shares_type', 'amount', 'price']


class PlayerCompaniesSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    name = serializers.CharField(source="company.name")
    ticker = serializers.CharField(source="company.ticker")
    dividendes = serializers.CharField(source="company.dividendes_percent")
    price = serializers.DecimalField(source="company.company_price", max_digits=10, decimal_places=2)
    co_shares = serializers.CharField(source="company.shares_amount")  # ordinary shares
    cp_shares = serializers.CharField(source="company.preferred_shares_amount")  # preferred shares

    class Meta:
        model = PlayerCompanies
        fields = ['type', 'name', 'price', 'ticker', 'shares_amount', 'preferred_shares_amount',
                  'dividendes', 'co_shares', 'cp_shares', 'isFounder', 'isHead']

    def get_type(self, obj):
        return obj.company.type.get_type_display()


class WarehouseSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = CompanyWarehouse
        fields = ['type', 'amount', 'max_amount']

    def get_type(self, obj):
        return obj.product.get_type_display()


class WarehouseUpdateSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    ticker = serializers.CharField(source='company.ticker', read_only=True)

    class Meta:
        model = CompanyWarehouse
        fields = ['ticker', 'amount', 'type']

    def get_type(self, obj):
        return obj.product.get_type_display()


class GoldSilverRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldSilverExchange
        fields = ['base_price', 'current_price', 'amount']


class GoldAmountSerializer(serializers.Serializer):
    amount = serializers.IntegerField()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero, clown")
        return value


class ProductsSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(source="product.type")
    name = serializers.SerializerMethodField()

    class Meta:
        model = ProductsExchange
        fields = ['name', 'purchase_price', 'sale_price', 'type']

    def get_name(self, obj):
        return obj.product.get_type_display()


class ProductsTradingSerializer(serializers.Serializer): # probably redo
    amount = serializers.IntegerField()
    ticker = serializers.CharField(max_length=8, min_length=4)
    type = serializers.ChoiceField(choices=ProductTypes.choices) # product type

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero, clown")
        return value

    def validate_ticker(self, value):
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
    wealth = serializers.DecimalField(max_digits=100, decimal_places=2, read_only=True)

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


class SharesExchangeWholesaleReceiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharesWholesaleTrade
        fields = ['desired_quantity', 'shares_type', 'reserved_money']


class SharesExchangeWholesaleSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharesWholesaleTrade
        fields = '__all__'
