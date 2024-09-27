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
    #апи для получения истории акций(тут тоже надо будет сделать несколько учитывая частичность обновления -
    #первый будет для ежедневного пользования, а второй будет вебхуком для постоянного мониторинга)
    #покупка акций(два вида), изменение в компании(сделать правильно чтобы менялся один параметр а не все)
]
