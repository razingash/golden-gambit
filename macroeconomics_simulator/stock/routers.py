from django.urls import path

from stock.consumers import *

router_urlpatterns = [
    path('ws/top-players-wealth/', TopUsersConsumer.as_asgi()),
    path('ws/top-companies-wealth/', TopCompaniesConsumer.as_asgi()),
]
