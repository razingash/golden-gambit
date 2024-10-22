from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.mixins import ListModelMixin
from djangochannelsrestframework.observer import model_observer

from services.critical_services import get_top_users_wealth
from stock.models import Player
from stock.serializers import TopPlayerSerializer


class WealthConsumer(GenericAsyncAPIConsumer, ListModelMixin):
    queryset = get_top_users_wealth

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        print(f"Ignoring incoming message: {text_data}")
        return

    async def receive_json(self, content, **kwargs):
        print(f"Ignoring incoming message: {content}")
        await self.send_json({"error": "Incoming messages are not allowed."})

    @model_observer(Player, serializer_class=TopPlayerSerializer)
    async def player_activity(self, message, observer=None, **kwargs):
        print(f"Received message from observer: {message}")
        await self.send_json(message)

    async def connect(self):
        print("WebSocket connected")
        await self.player_activity.subscribe()
        await super().connect()

    async def disconnect(self, code):
        print("WebSocket disconnected")
        await self.player_activity.unsubscribe()
        await super().disconnect(code)

