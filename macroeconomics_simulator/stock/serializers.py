from django.contrib.auth import get_user_model
from rest_framework import serializers

from stock.models import Player, Company, PlayerCompanies, StateLaw, GlobalEvent, CompanyWarehouse, GoldSilverExchange, \
    ProductsExchange
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
    type = serializers.CharField(source='type.type')
    cartoonist = serializers.IntegerField(source='type.cartoonist')

    class Meta:
        model = Company
        fields = ['type', 'cartoonist', 'ticker', 'name', 'shares_amount', 'preferred_shares_amount', 'share_price',
                  'silver_reserve', 'gold_reserve', 'company_price', 'dividendes_percent', 'founding_date']


class CompanyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name', 'shares_amount', 'preferred_shares_amount', 'dividendes_percent')

    def update(self, instance, validated_data):
        if 'name' in validated_data:
            instance.name = validated_data.get('name', instance.name)

        if 'shares_amount' in validated_data:
            self.update_shares_amount(instance, validated_data['shares_amount'])

        if 'preferred_shares_amount' in validated_data:
            self.update_preferred_shares_amount(instance, validated_data['preferred_shares_amount'])

        if 'dividendes_percent' in validated_data:
            self.update_dividendes_percent(instance, validated_data['dividendes_percent'])

        instance.save()
        return instance
    # видимо надо будет разделить сервисы на несколько папок чтобы не было неразберихи
    def update_shares_amount(self, instance, shares_amount):
        pass # тут надо будет делать перераспределение акций - сделать после добавления функции покупки акций(то есть в конце)

    def update_preferred_shares_amount(self, instance, preferred_shares_amount):
        pass # по идее повышатся будет после того как владелец внесет голду на счет компании или люди купят акции за золото(которое пойдет компании)

    def update_dividendes_percent(self, instance, dividendes_percent):
        pass # сделать фиксированое колебание - максимум на 0.5 в год


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['type', 'ticker', 'name', 'shares_amount', 'preferred_shares_amount', 'dividendes_percent']


class CompanyCreateSerializer2(serializers.ModelSerializer):
    type = serializers.CharField(source='type.type')
    cartoonist = serializers.IntegerField(source='type.cartoonist')

    class Meta:
        model = Company
        fields = ['type', 'cartoonist', 'ticker', 'shares_amount', 'preferred_shares_amount', 'dividendes_percent']

class PlayerCompaniesSerializer(serializers.ModelSerializer):
    company = CompanyCreateSerializer2()

    class Meta:
        model = PlayerCompanies
        fields = ['company', 'shares_amount', 'preferred_shares_amount', 'isFounder', 'isHead']


class WarehouseSerializer(serializers.ModelSerializer):
    product_type_display = serializers.SerializerMethodField()

    class Meta:
        model = CompanyWarehouse
        fields = ['company', 'amount', 'product_type_display']

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


class LawsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateLaw
        fields = '__all__'


class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalEvent
        fields = '__all__'
