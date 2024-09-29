from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

urlpatterns = [
    path('v1/registration/', RegisterView.as_view(), name='register'),
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/token/verify/', TokenVerifyWithBlacklistView.as_view(), name='token_verify'),
    path('v1/logout/', LogoutView.as_view(), name='logout'),
    path('v1/users/<str:user_id>/', UserApiView.as_view(), name='user'), # get
    path('v1/users/<int:user_id>/companies/', UserCompaniesView.as_view(), name='user_companies'), # get | post
    path('v1/companies/', CompanyListView.as_view(), name='companies'), # | get
    path('v1/companies/<str:ticker>/', CompanyApiView.as_view(), name='company'), # get | patch | delete?
    path('v1/companies/<str:ticker>/warehouse/', CompanyWarehouseApiView.as_view(), name='company_warehouse'), # | get
    path('v1/companies/<str:ticker>/warehouse/update/', CompanyWarehouseUpdateApiView.as_view(), name='company_warehouse_update'), # | get
    path('v1/companies/<str:ticker>/sell-shares/<int:shares_type>/', CompanySellShareApiView.as_view(), name='company_sell_shares'), # | get | post | delete
    path('v1/companies/<str:ticker>/history/', CompanyHistoryApiView.as_view(), name='company_history'), # | get
    path('v1/stock/gold/', StockGoldApiView.as_view(), name='gold_to_silver_actual_price'), # get
    path('v1/stock/gold/history/', StockGoldHistoryApiView.as_view(), name='gold_to_silver_history'), # get
    path('v1/stock/gold/<str:transaction_type>/', GoldExchangeApiView.as_view(), name='gold-exchange'), # post
    path('v1/stock/products/', StockProductsApiView.as_view(), name='products-exchange'), # get
    path('v1/stock/products/<int:transaction_type>/', ProductsExchangeApiView.as_view(), name='products-exchange'), # post
    #path('v1/stock/shares-exchange/<int:transaction_type>/', ShagesExchange.as_view(), name='shares-exchange'), # get | post
    path('v1/laws/', LawsApiView.as_view(), name='laws'), # get
    path('v1/events/', EventsApiView.as_view(), name='events') # get
]

"""
0) Добавить возможность прокачки компании
1) добавить permissions для проверки является ли пользователь который запрашивает инфу её автором
и возможно еще один для компаний - является ли пользователь акционером
3) апи для биржи
4) апи для акций(самый гемор)
5)вебхуки для мониторинга цен компании, золота
* попутно можно разделить сервисы на несколько файлов чтобы не было этой чепухи
"""
