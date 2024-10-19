from django.urls import path

from stock.consumers import *

routerpatterns = [
    path('ws/player-wealth/', WealthConsumer.as_asgi()),
]
