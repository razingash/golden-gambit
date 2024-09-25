from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

urlpatterns = [
    path('v1/registration/', RegisterView.as_view(), name='register'),
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/token/verify/', TokenVerifyWithBlacklistView.as_view(), name='token_verify'),
    path('v1/logout/', LogoutView.as_view(), name='logout')
]
