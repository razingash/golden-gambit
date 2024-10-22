import asyncio
import json
import os
import random
import time

from celery import shared_task
from channels.layers import get_channel_layer
from django.db import transaction

from macroeconomics_simulator import settings
from stock.models import GoldSilverExchange, Player

"""
in order to trigger periodic tasks or events for websockets, you need to import model
"""
from stock.consumers import WealthConsumer


@shared_task # redis
def document_gold_silver_rate():
    gold_silver_stock = GoldSilverExchange.objects.afirst()

    json_path = os.path.join(settings.MEDIA_ROOT, 'gold_silver_rate', f"{gold_silver_stock.id}.json")

    with open(json_path, 'r') as file:
        json_data = json.load(file)

    json_data["contents"].append({
        "timestamp": int(time.time()),
        "current price": float(round(gold_silver_stock.current_price, 2))
    })

    with open(json_path, 'w') as file:
        json.dump(json_data, file, indent=2)

@shared_task # rabbitMQ
def dividends_payment():
    pass


""" testing(using redis) """
@shared_task
def check_layer():
    channel_layer = get_channel_layer()
    print(channel_layer)
    return channel_layer

@shared_task
def rand_user_gold(): # test
    new_gold = random.randint(1, 11)
    player_id = random.randint(1, 11)
    player = Player.objects.get(id=player_id)
    player.gold = new_gold
    player.save()


@shared_task
def update_player_gold(player_id, new_gold):
    player = Player.objects.get(id=player_id)
    player.gold = new_gold

    with transaction.atomic():
        player.save()

    return player


@shared_task
def rand_user_silver():
    user_id = random.randint(1, 11)
    player = Player.objects.get(id=user_id)
    player.silver = random.randint(10000, 30000)
    player.save()
    return player

@shared_task
def rand_users_gold():
    players = Player.objects.all()
    for player in players:
        player.gold = random.randint(1, 30)
        player.save()

@shared_task
async def rand_users_gold_2(): # with sleeping
    players = Player.objects.all()
    for player in players:
        await asyncio.sleep(2)
        player.gold = random.randint(1, 30)
        player.save()

