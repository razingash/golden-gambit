from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.mixins import ListModelMixin
from djangochannelsrestframework.observer import model_observer

from services.critical_services import get_top_users_wealth
from stock.models import Player
from stock.serializers import TopPlayerSerializer

"""
возможно остался микробаг - player_activity_groups срабатывает на обновления всех объектов модели, но обновления высылаются
только необходимым, так что скорее всего так и должно быть
"""
class WealthConsumer(GenericAsyncAPIConsumer, ListModelMixin): # сделать закрытие соединения если пользователь отправляет сообщение
    @model_observer(Player, serializer_class=TopPlayerSerializer)
    async def player_activity(self, message, observer=None, **kwargs):
        print(f"Received message from observer: {message}")
        await self.send_json(message)

    @player_activity.groups_for_signal
    def player_activity_groups(self, instance: Player, **kwargs): # DO NOT DO DATABASE QURIES HERE
        print(f"Creating group for player {instance.id}")
        yield f'player_{instance.id}'

    @player_activity.groups_for_consumer # This is called when someone subscribes/unsubscribes
    def player_activity_groups_for_consumer(self, player=None, **kwargs):
        if isinstance(player, Player): # if the user sends the data then player will be equal to player.id
            yield f'player_{player.id}'

    @action()
    async def subscribe_to_top_players(self, **kwargs): # работает
        top_users = await get_top_users_wealth()
        self.subscribed_players = [user.id for user in top_users]

        print(f"Subscribing to top players: {self.subscribed_players}")

        for user in top_users:
            await self.player_activity.subscribe(player=user)

    async def connect(self):
        print("WebSocket connected")
        await self.subscribe_to_top_players()
        await super().connect()

    async def disconnect(self, code):
        print("WebSocket disconnected")
        if hasattr(self, 'subscribed_players'):
            for player_id in self.subscribed_players:
                await self.player_activity.unsubscribe(player=player_id)
        await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        #print(f"Unexpected incoming message in TopUsersHook: {text_data}")
        await self.close(1000, "ping doesn't pong")

    async def receive_json(self, content, **kwargs):
        #print(f"Unexpected incoming json message in TopUsersHook: {content}")
        await self.close(1000, "ping doesn't pong")
