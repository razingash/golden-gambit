from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from stock.models import Player, Company, PlayerCompanies, StateLaw, GlobalEvent, CompanyWarehouse, GoldSilverExchange, \
    ProductsExchange, SharesExchange
from stock.utils import ProductTypes


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        player = Player.objects.create_user(username=validated_data['username'], password=validated_data['password'])
        return player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'silver', 'gold', 'last_login', 'date_joined']


# сделать три уровня доступа к сериализатору(разделить на три разных или найти лучший способ)
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


class CompanyCreateSerializer2(serializers.ModelSerializer):
    company_type_display = serializers.SerializerMethodField()
    cartoonist = serializers.IntegerField(source='type.cartoonist')

    class Meta:
        model = Company
        fields = ['company_type_display', 'cartoonist', 'ticker', 'shares_amount', 'preferred_shares_amount', 'dividendes_percent']

    def get_company_type_display(self, obj):
        return obj.type.get_type_display()


class PlayerCompaniesSerializer(serializers.ModelSerializer):
    company = CompanyCreateSerializer2()

    class Meta:
        model = PlayerCompanies
        fields = ['company', 'shares_amount', 'preferred_shares_amount', 'isFounder', 'isHead']


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
