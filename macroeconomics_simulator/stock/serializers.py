from datetime import timedelta
from decimal import Decimal
from re import sub as re_sub

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from stock.models import Player, Company, PlayerCompanies, StateLaw, GlobalEvent, CompanyWarehouse, GoldSilverExchange, \
    ProductsExchange, SharesExchange, CompanyRecipe, SharesWholesaleTrade
from stock.utils.utils_models import ProductTypes


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
    cartoonist = serializers.IntegerField(source='type.cartoonist')

    class Meta:
        model = Company
        fields = ['type', 'cartoonist', 'ticker', 'name', 'shares_amount', 'preferred_shares_amount', 'share_price',
                  'silver_reserve', 'gold_reserve', 'company_price', 'dividendes_percent', 'founding_date']


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
        last_update = instance.dividendes_change_date
        current_time = timezone.now()

        if dividendes_percent <= 0:
            raise serializers.ValidationError({'dividendes_percent': f"Too low fluctuation - {dividendes_percent}%"})

        if current_time - last_update < timedelta(days=1):
            raise serializers.ValidationError({'dividendes_percent': "Dividends can only be changed once per day"})

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

    @staticmethod
    def validate_ticker(value):
        new_ticker = re_sub(r'[^a-zA-Z0-9]', '', value).upper()
        if len(new_ticker) < 3 or len(new_ticker) > 8:
            raise serializers.ValidationError('ticker must be from 4 to 8 characters')
        return new_ticker

    @staticmethod
    def validate_type(value):
        if value.type in [1, 2, 3, 4, 5, 6, 7]:
            return value.type
        raise serializers.ValidationError("Registration of new tickers is only available in the primary sector")

    @staticmethod
    def validate_shares_amount(value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero, clown")
        return value

    @staticmethod
    def validate_preferred_shares_amount(value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero, clown")
        return value

    @staticmethod
    def validate_dividendes_percent(value):
        if 10 > value < 2:
            raise serializers.ValidationError("Dividendes percent must be greater or equal 2 and less than 10")
        return value


class CompanyPrintNewSharesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['ticker', 'shares_amount', 'preferred_shares_amount']


class CompanyConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['ticker', 'company_price']


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

class SharesExchangeSerializer(serializers.ModelSerializer): # used in 2 places!
    class Meta:
        model = SharesExchange
        fields = ['id', 'shares_type', 'amount', 'price']


class SharesPurchaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

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

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(PlayerCompaniesSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def get_type(self, obj):
        return obj.company.type.type


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyWarehouse
        fields = ['product', 'amount', 'max_amount']


class WarehouseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyWarehouse
        fields = ['amount', 'product'] # no need for ticker for now


class GoldSilverRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldSilverExchange
        fields = ['current_price', 'amount']


class GoldSilverRateStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldSilverExchange
        fields = ['current_price', 'amount']


class GoldAmountSerializer(serializers.Serializer):
    amount = serializers.IntegerField()

    @staticmethod
    def validate_amount(value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero, clown")
        return value


class ProductsSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(source="product.type")

    class Meta:
        model = ProductsExchange
        fields = ['purchase_price', 'sale_price', 'type']


class ProductsTradingSerializer(serializers.Serializer): # probably redo
    amount = serializers.IntegerField()
    ticker = serializers.CharField(max_length=8, min_length=4)
    type = serializers.ChoiceField(choices=ProductTypes.choices) # product type

    @staticmethod
    def validate_amount(value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero, clown")
        return value

    @staticmethod
    def validate_ticker(value):
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
        fields = ['type', 'state', 'description']


class TopPlayerSerializer(serializers.ModelSerializer): # could be useless later
    wealth = serializers.DecimalField(max_digits=100, decimal_places=2, read_only=True)

    class Meta:
        model = Player
        fields = ['username', 'silver', 'gold', 'wealth']


class IngredientSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = CompanyRecipe
        fields = ['type', 'amount']

    def get_type(self, obj):
        return obj.ingredient.type


class CompanyRecipesSerializer(serializers.ModelSerializer):
    company_type = serializers.IntegerField(source="recipe.company_type")
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = CompanyRecipe
        fields = ['recipe', 'company_type', 'ingredients']

    def get_ingredients(self, obj):
        company_recipes = CompanyRecipe.objects.filter(recipe=obj.recipe)
        return IngredientSerializer(company_recipes, many=True).data


class CompanyTransmutationSerializer(serializers.Serializer):
    tickers = serializers.ListField(child=serializers.CharField(max_length=8, min_length=4), write_only=True)
    recipe_id = serializers.IntegerField(write_only=True)
    name = serializers.CharField(max_length=120, write_only=True)
    dividendes_percent = serializers.DecimalField(max_digits=4, decimal_places=2, write_only=True)
    ticker = serializers.CharField(max_length=8, min_length=4, write_only=True)

    class Meta:
        fields = ['tickers', 'ticker', 'recipe_id', 'name', 'dividendes_percent']

    @staticmethod
    def validate_dividendes_percent(value):
        if 10 > value < 2:
            raise serializers.ValidationError("Dividendes percent must be greater or equal 2 and less than 10")
        return value


class SharesExchangeWholesaleReceiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharesWholesaleTrade
        fields = ['desired_quantity', 'shares_type', 'reserved_money']


class SharesExchangeWholesaleSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharesWholesaleTrade
        fields = '__all__'
