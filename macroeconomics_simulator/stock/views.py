import asyncio

from django.db.models import Q
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.views import TokenVerifyView

from services.base import get_paginated_objects, get_object, paginate_objects
from services.critical_services import get_current_gold_silver_rate
from services.company.C_services import create_new_company, get_company_inventory, update_produced_products_amount, \
    make_new_shares, put_up_shares_for_sale, get_company_history, buy_products, sell_products, get_top_companies, \
    get_available_recipes, merge_companies
from services.general_services import get_current_events
from services.stock.S_services import purchase_gold, sell_gold, get_gold_history, get_available_company_shares, \
    buy_shares, buy_management_shares, buy_shares_wholesale, get_shares_on_stock_for_wholesale
from services.user.U_services import get_player, get_user_companies, get_top_users, get_user_shares
from stock.utils.exceptions import custom_exception
from stock.models import Company, StateLaw, GlobalEvent, GoldSilverExchange, ProductsExchange
from stock.permissions import IsHeadOfCompany, IsHeadOfSelectedCompany
from stock.serializers import RegisterSerializer, CompanyCreateSerializer, CompanySerializer, PlayerSerializer, \
    PlayerCompaniesSerializer, CompanyUpdateSerializer, EventsSerializer, LawsSerializer, WarehouseSerializer, \
    GoldSilverRateSerializer, GoldAmountSerializer, ProductsSerializer, ProductsTradingSerializer, \
    SharesExchangeSerializer, SharesExchangeListSerializer, CompanyPrintNewSharesSerializer, SellSharesSerializer, \
    TopPlayerSerializer, CompanyRecipesSerializer, SharesExchangeWholesaleReceiveSerializer, \
    SharesExchangeWholesaleSendSerializer, DividedCompanySerializer, WarehouseUpdateSerializer, \
    SharesExchangeWholesaleListSerializer, CompanyTransmutationSerializer, SharesPurchaseSerializer, \
    GoldSilverRateStreamSerializer
from stock.utils.utils_models import remove_company_recipes_duplicates


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
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        player = get_player(request.user.id)

        return Response(PlayerSerializer(player, many=False).data)


class UserCompaniesView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        fields = request.query_params.get('fields')
        if fields:
            fields = fields.split(',')

        companies, has_next = get_user_companies(request.user.id, request.query_params, fields=fields)

        serializer = PlayerCompaniesSerializer(companies, many=True, fields=fields)
        return Response({"data": serializer.data, "has_next": has_next})

    @custom_exception
    def post(self, request):
        serializer = CompanyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = create_new_company(user_id=request.user.id, request_data=serializer.validated_data)

        return Response(CompanySerializer(company, many=False).data)


class UserSharesView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request): # After completely setting up the frontend, check the required fields again
        shares, has_next = get_user_shares(request.user.id, request.query_params)
        serializer = PlayerCompaniesSerializer(shares, many=True)

        return Response({"data": serializer.data, "has_next": has_next})


class CompanyListView(APIView):
    def get(self, request):
        companies, has_next = get_paginated_objects(model=Company, query_params=request.query_params)
        serializer = CompanySerializer(companies, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})


class CompanyRecipes(APIView): # no need for unauthorized users
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        recipes = get_available_recipes()
        recipes = remove_company_recipes_duplicates(CompanyRecipesSerializer(recipes, many=True).data)
        return Response(recipes)

    @custom_exception
    def post(self, request):
        serializer = CompanyTransmutationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        merge_companies(request.user.id, serializer.validated_data)

        return Response(status=status.HTTP_200_OK)


class CompanyApiView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]

        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsHeadOfCompany()]

        return super().get_permissions()

    def get(self, request, ticker):
        company = get_object_or_404(Company, ticker=ticker)

        return Response(DividedCompanySerializer(company, context={'user': request.user}, many=False).data)

    def patch(self, request, ticker):
        company = get_object_or_404(Company, ticker=ticker)
        serializer = CompanyUpdateSerializer(company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)


class CompanyWarehouseApiView(APIView): # check
    """only receiving the company's inventory, putting it up for sale in another API"""
    permission_classes = (IsAuthenticated, IsHeadOfCompany)

    def get(self, request, ticker):
        inventory = get_company_inventory(ticker)
        return Response(WarehouseSerializer(inventory, many=True).data)

class CompanyWarehouseUpdateApiView(APIView):
    """updates the quantity of the selected resource produced by the company"""
    permission_classes = (IsAuthenticated, IsHeadOfCompany)

    def get(self, request, ticker):
        updated_products = update_produced_products_amount(ticker)
        return Response(WarehouseUpdateSerializer(updated_products, many=True).data)


class CompanyPrintNewSharesApiView(APIView):
    """
    prints shares at the selected price and immediately puts them up for sale.
    Yes, it’s incorrect that the user himself sets the price for ordinary shares, but this was done on purpose
    """
    permission_classes = (IsAuthenticated, IsHeadOfCompany)

    def post(self, request, ticker): # issue of new shares
        serializer = SharesExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shares_type = serializer.validated_data.get('shares_type')
        amount = serializer.validated_data.get('amount')
        price = serializer.validated_data.get('price')
        user_id = request.user.id

        if shares_type == 1 or shares_type == 2: # 1 - ordinary shares & 2 - management shares
            obj = make_new_shares(user_id, ticker, shares_type, amount, price)
            return Response(CompanyPrintNewSharesSerializer(obj, many=False).data)
        else: # error
            return Response(f'error: Bad Request, {shares_type} is a non-existent share type', status=status.HTTP_400_BAD_REQUEST)


class CompanySellShareApiView(APIView):
    permission_classes = (IsAuthenticated, )

    @custom_exception
    def post(self, request, ticker):
        """
        putting up management shares for an internal auction - 1 hour are given to The Head of the company to buy back the
        shares or cancel the sale, then 6 hours will be given for shareholders, after which they will go to the stock exchange
        """
        serializer = SharesExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shares_type = serializer.validated_data.get('shares_type')
        amount = serializer.validated_data.get('amount')
        price = serializer.validated_data.get('price')
        user_id = request.user.id

        if shares_type == 1 or shares_type == 2: # 1 - ordinary shares & 2 - management shares
            company = Company.objects.filter(ticker=ticker).only('id').first()
            if company is None:
                return Response(f'Company with ticker {ticker} does not exists')
            shares = put_up_shares_for_sale(user_id, company.id, shares_type, amount, price)
            return Response(SellSharesSerializer(shares, many=False).data)
        else: # error
            return Response(f'error: Bad Request, {shares_type} is a non-existent share type', status=status.HTTP_400_BAD_REQUEST)


class CompanyHistoryApiView(APIView):
    """provides company data that is updated every few hours"""
    @custom_exception
    def get(self, request, ticker):
        json_company_history = get_company_history(ticker)
        return Response(json_company_history)


class StockGoldApiView(APIView):
    """needed to set the initial price in case SSE does not work"""
    def get(self, request): # getting gold/silver rate history
        gold_rate = get_object(model=GoldSilverExchange, condition=Q(id=1), fields=['current_price', 'amount'])

        return Response(GoldSilverRateSerializer(gold_rate, many=False).data)


class GoldExchangeApiView(APIView):
    permission_classes = (IsAuthenticated, )

    @custom_exception
    def post(self, request, transaction_type): # if the user doesn't have enough money a custom exception will occur
        serializer = GoldAmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get('amount')

        user_id = request.user.id

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
    permission_classes = (IsAuthenticated, IsHeadOfSelectedCompany)

    @custom_exception
    def post(self, request, transaction_type):  # if the user doesn't have enough money a custom exception will occur
        serializer = ProductsTradingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get('amount')
        company_ticker = serializer.validated_data.get('ticker')
        product_type = serializer.validated_data.get('type')

        if transaction_type == "buy":  # purchase
            buy_products(company_ticker, product_type, amount)
            return Response(status=status.HTTP_200_OK)
        elif transaction_type == "sell":  # selling
            sell_products(company_ticker, product_type, amount)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(f'error: Bad Request, {transaction_type} is a non-existent transaction type',
                            status=status.HTTP_400_BAD_REQUEST)


class SharesWholesaleListApiView(APIView): # make webhook for getting actual amount of available shares?
    """don't show duplicates, related with wholesale"""
    def get(self, request):
        shares, has_next = get_shares_on_stock_for_wholesale(query_params=request.query_params)
        serializer = SharesExchangeWholesaleListSerializer(shares, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})


class SharesExchangeApiView(APIView): # shares sale in CompanySellShareApiView
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]

        if self.request.method == 'POST':
            return [IsAuthenticated()]

        return super().get_permissions()

    def get(self, request, ticker): # returns shares that the company trades
        shares, has_next = get_available_company_shares(ticker=ticker, query_params=request.query_params,
                                                        user_id=request.user.id)
        serializer = SharesExchangeListSerializer(shares, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})

    @custom_exception
    def post(self, request, ticker): # only purchase
        serializer = SharesPurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shares_type = serializer.validated_data.get('shares_type')
        amount = serializer.validated_data.get('amount')
        price = serializer.validated_data.get('price')
        pk = serializer.validated_data.get('id')
        user_id = request.user.id

        if shares_type == 1: # ordinary
            buy_shares(user_id, ticker, amount, price, pk)
            return Response(status=status.HTTP_200_OK)
        elif shares_type == 2: # management
            buy_management_shares(user_id, ticker, amount, price, pk)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(f'error: Bad Request, {shares_type} is a non-existent shares type', status=status.HTTP_400_BAD_REQUEST)


class SharesExchangeWholesaleApiView(APIView):
    permission_classes = (IsAuthenticated, )

    @custom_exception
    def post(self, request, ticker):
        serializer = SharesExchangeWholesaleReceiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data.get('desired_quantity')
        offered_money = serializer.validated_data.get('reserved_money')
        shares_type = serializer.validated_data.get('shares_type')

        user_id = request.user.id
        purchased_shares = buy_shares_wholesale(user_id, ticker=ticker, amount=amount, offered_money=offered_money,
                                                shares_type=shares_type)

        return Response(SharesExchangeWholesaleSendSerializer(purchased_shares, many=False).data)


class LawsApiView(APIView):
    def get(self, request):
        laws, has_next = get_paginated_objects(model=StateLaw, query_params=request.query_params)
        serializer = LawsSerializer(laws, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})

class EventsApiView(APIView):
    def get(self, request):
        objects = get_current_events()

        events, has_next = paginate_objects(objects=objects, query_params=request.query_params)
        serializer = EventsSerializer(events, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})


class TopCompaniesApiView(APIView):
    def get(self, request): # cache request
        top_companies = get_top_companies()

        return Response(top_companies)

class TopUsersApiView(APIView):
    def get(self, request): # cache request
        top_users = get_top_users()

        return Response(TopPlayerSerializer(top_users, many=True).data)


async def actual_gold_price_sse_stream(request):
    """Danger Zone"""
    async def event_stream():
        while True:
            await asyncio.sleep(5)
            serializer = GoldSilverRateStreamSerializer(await get_current_gold_silver_rate())
            yield f"data: {serializer.data}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'

    return response
