from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

urlpatterns = [
    path('v1/registration/', RegisterView.as_view(), name='register'),
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/token/verify/', TokenVerifyWithBlacklistView.as_view(), name='token_verify'),
    path('v1/logout/', LogoutView.as_view(), name='logout'),
    path('v1/user/', UserApiView.as_view(), name='user_info'), # get
    path('v1/user/companies/', UserCompaniesView.as_view(), name='user_companies'), # get | post
    path('v1/user/shares/', UserSharesView.as_view(), name='user_companies'), # get
    path('v1/companies/', CompanyListView.as_view(), name='companies'), # get
    path('v1/companies/recipes/', CompanyRecipes.as_view(), name='companies-recipes'), # get
    path('v1/companies/<str:ticker>/', CompanyApiView.as_view(), name='company'), # get | patch
    path('v1/companies/<str:ticker>/warehouse/', CompanyWarehouseApiView.as_view(), name='company_warehouse'), # | get
    path('v1/companies/<str:ticker>/warehouse/update/', CompanyWarehouseUpdateApiView.as_view(), name='company_warehouse_update'), # | get
    path('v1/companies/<str:ticker>/exchange/', CompanyIncreaseSharesApiView.as_view(), name='company_increase_shares'), # post
    path('v1/companies/<str:ticker>/sell-shares/', CompanySellShareApiView.as_view(), name='company_sell_shares'), # post
    path('v1/companies/<str:ticker>/history/', CompanyHistoryApiView.as_view(), name='company_history'), # get
    path('v1/stock/gold/', StockGoldApiView.as_view(), name='gold_to_silver_actual_price'), # get
    path('v1/stock/gold/history/', StockGoldHistoryApiView.as_view(), name='gold_to_silver_history'), # get
    path('v1/stock/gold/<str:transaction_type>/', GoldExchangeApiView.as_view(), name='gold-exchange'), # post
    path('v1/stock/products/', StockProductsApiView.as_view(), name='products-pricing'), # get
    path('v1/stock/products/<str:transaction_type>/', ProductsExchangeApiView.as_view(), name='products-exchange'), # post
    path('v1/stock/shares-exchange/', SharesListApiView.as_view(), name='shares-list'), # get
    path('v1/stock/shares-exchange/<str:ticker>/', SharesExchangeApiView.as_view(), name='shares-exchange'), # get | post
    path('v1/stock/shares-exchange/<str:ticker>/wholesale/', SharesExchangeWholesaleApiView.as_view(), name='shares-exchange-wholesale'), # post
    path('v1/laws/', LawsApiView.as_view(), name='laws'), # get
    path('v1/events/', EventsApiView.as_view(), name='events'), # get
    path('v1/top/companies/', TopCompaniesApiView.as_view(), name='top-companies'), # get
    path('v1/top/users/', TopUsersApiView.as_view(), name='top-users') # get
]
