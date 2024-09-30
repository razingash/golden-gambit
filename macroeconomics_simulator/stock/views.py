from django.db.models import Q
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.views import TokenVerifyView

from stock.models import Company, StateLaw, GlobalEvent, GoldSilverExchange, ProductsExchange
from stock.serializers import RegisterSerializer, CompanyCreateSerializer, CompanySerializer, PlayerSerializer, \
    PlayerCompaniesSerializer, CompanyUpdateSerializer, EventsSerializer, LawsSerializer, WarehouseSerializer, \
    GoldSilverRateSerializer, GoldAmountSerializer, ProductsSerializer, ProductsTradingSerializer, \
    CompanySharesForSaleSerializer, SharesExchangePurchaseSerializer, SharesExchangeListSerializer
from stock.services import create_new_company, get_player, get_user_companies, get_paginated_objects, \
    get_company_history, get_company_inventory, get_object, get_gold_history, purchase_gold, sell_gold, sell_products, \
    buy_products, update_produced_products_amount, make_new_shares, put_up_shares_for_sale, get_available_shares, \
    buy_shares, buy_management_shares
from stock.utils import custom_exception


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            player = serializer.save()

            refresh = RefreshToken.for_user(player)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({'refresh': refresh_token, 'access': access_token})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)

            if token.payload['user_id'] != request.user.id: #
                return Response({"INFO": "Invalid token during logout"}, status=status.HTTP_403_FORBIDDEN)

            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except (TokenError, InvalidToken):
            return Response({"detail": "Invalid token during logout."}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)


class TokenVerifyWithBlacklistView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        try:
            token = UntypedToken(request.data['token'])

            if BlacklistedToken.objects.filter(token__jti=token.payload['jti']).exists():
                raise InvalidToken({"detail": "This token has been canceled"})

            return super().post(request, *args, **kwargs)
        except TokenError as e:
            raise InvalidToken(e.args[0])


class UserApiView(APIView):
    #add some permissions
    def get(self, request, user_id):
        player = get_player(user_id)

        return Response(PlayerSerializer(player, many=False).data)


class UserCompaniesView(APIView):
    #permission_classes = (IsAuthenticated, )

    def get(self, request, user_id):
        companies = get_user_companies(user_id)

        return Response(PlayerCompaniesSerializer(companies, many=True).data)

    @custom_exception
    def post(self, request, user_id):
        serializer = CompanyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = create_new_company(user_id=user_id, request_data=request.data)

        return Response(CompanySerializer(company, many=False).data)


class CompanyListView(APIView):
    def get(self, request):
        companies, has_next = get_paginated_objects(model=Company, query_params=request.query_params)
        serializer = CompanySerializer(companies, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})


class CompanyApiView(APIView):
    def get(self, request, ticker):
        company = get_object_or_404(Company, ticker=ticker)

        return Response(CompanySerializer(company, many=False).data)

    def patch(self, request, ticker):
        company = get_object_or_404(Company, ticker=ticker)
        serializer = CompanyUpdateSerializer(company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)


class CompanyWarehouseApiView(APIView): # check
    """only receiving the company's inventory, putting it up for sale in another API"""
    def get(self, request, ticker):
        inventory = get_company_inventory(ticker)
        return Response(WarehouseSerializer(inventory, many=True).data)

class CompanyWarehouseUpdateApiView(APIView):
    """updates the quantity of the selected resource produced by the company"""
    #permission_classes = (IsAuthenticated, IsAuthor)
    def get(self, request, ticker):
        updated_products = update_produced_products_amount(ticker)
        return Response(WarehouseSerializer(updated_products, many=True).data)


class CompanyIncreaseSharesApiView(APIView):
    # добавить проверку на авторство(на уровне главы компании)
    def post(self, request, ticker, shares_type): # issue of new shares
        serializer = CompanySharesForSaleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = request.data.get('amount')
        price = request.data.get('price')

        if shares_type == 1 or shares_type == 2: # 1 - ordinary shares & 2 - management shares
            make_new_shares(ticker, shares_type, amount, price)
        else: # error
            return Response(f'error: Bad Request, {shares_type} is a non-existent share type', status=status.HTTP_400_BAD_REQUEST)


class CompanySellShareApiView(APIView):
    def post(self, request, ticker, shares_type):
        """
        putting up management shares for an internal auction - 1 hour are given to The Head of the company to buy back the
        shares or cancel the sale, then 6 hours will be given for shareholders, after which they will go to the stock exchange
        """
        if shares_type == 1 or shares_type == 2: # 1 - ordinary shares & 2 - management shares
            put_up_shares_for_sale(ticker, shares_type)
        else: # error
            return Response(f'error: Bad Request, {shares_type} is a non-existent share type', status=status.HTTP_400_BAD_REQUEST)


class CompanyHistoryApiView(APIView):
    """provides company data that is updated every few hours"""
    @custom_exception
    def get(self, request, ticker):
        json_company_history = get_company_history(ticker)
        return Response(json_company_history)


class StockGoldApiView(APIView):
    def get(self, request): # getting gold/silver rate history
        gold_rate = get_object(model=GoldSilverExchange, condition=Q(id=1))

        return Response(GoldSilverRateSerializer(gold_rate, many=False).data)


class GoldExchangeApiView(APIView):
    @custom_exception
    def post(self, request, transaction_type): # if the user doesn't have enough money a custom exception will occur
        serializer = GoldAmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = request.data.get('amount')
        user_id = request.data.get('user_id')  # позже сделать отдельный метод который будет получать id из токена
        if transaction_type == "buy": # purchase
            purchase_gold(user_id=user_id, amount=amount)

            return Response(status=status.HTTP_200_OK)
        elif transaction_type == "sell": # selling
            sell_gold(user_id=user_id, amount=amount)

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(f'error: Bad Request, {transaction_type} is a non-existent transaction type',
                            status=status.HTTP_400_BAD_REQUEST)


class StockGoldHistoryApiView(APIView):
    def get(self, request):
        json_gold_history = get_gold_history()
        return Response(json_gold_history)


class StockProductsApiView(APIView):
    """getting a list of products for sale"""
    def get(self, request):
        products, has_next = get_paginated_objects(model=ProductsExchange, query_params=request.query_params)
        serializer = ProductsSerializer(products, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})


class ProductsExchangeApiView(APIView):
    """buying or selling goods, while there is no point in buying (and isn't planned)"""

    @custom_exception
    def post(self, request, transaction_type):  # if the user doesn't have enough money a custom exception will occur
        serializer = ProductsTradingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = request.data.get('amount')
        company_ticker = request.data.get('company_ticker')
        product_type = request.data.get('product_type')

        if transaction_type == "buy":  # purchase
            buy_products(company_ticker, product_type, amount)
            return Response(status=status.HTTP_200_OK)
        elif transaction_type == "sell":  # selling
            sell_products(company_ticker, product_type, amount)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(f'error: Bad Request, {transaction_type} is a non-existent transaction type',
                            status=status.HTTP_400_BAD_REQUEST)


class SharesListApiView(APIView):
    def get(self, request):
        shares, has_next = get_available_shares(request.query_params, user_id=None)
        serializer = SharesExchangeListSerializer(shares, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})


class SharesExchangeApiView(APIView): # shares sale in CompanySellShareApiView
    """make webhook for getting actual amount of available shares"""

    @custom_exception
    def post(self, request, ticker, shares_type): # only purchase
        serializer = SharesExchangePurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = request.data.get('amount')
        price = request.data.get('price')
        user_id = request.data.get('user_id')  # позже сделать отдельный метод который будет получать id из токена
        if shares_type == 1: # ordinary
            buy_shares(user_id, ticker, amount, price)
            return Response(status=status.HTTP_200_OK)
        elif shares_type == 2: # management
            buy_management_shares(user_id, ticker, amount, price)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(f'error: Bad Request, {shares_type} is a non-existent shares type', status=status.HTTP_400_BAD_REQUEST)


class LawsApiView(APIView):
    def get(self, request):
        laws, has_next = get_paginated_objects(model=StateLaw, query_params=request.query_params)
        serializer = LawsSerializer(laws, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})

class EventsApiView(APIView):
    def get(self, request):
        events, has_next = get_paginated_objects(model=GlobalEvent, query_params=request.query_params)
        serializer = EventsSerializer(events, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})
