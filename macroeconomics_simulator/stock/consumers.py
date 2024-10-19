from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer

from services.critical_services import get_user_wealth


# откалибровать capacity
class WealthConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.player_id = self.scope['url_route']['kwargs']['player_id']
        self.group_name = f'wealth_{self.player_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_wealth_update(self, event):
        channel_layer = get_channel_layer()

        user = await get_user_wealth(self.player_id)

        wealth_data = {
            'username': user.username,
            'silver': str(user.silver),
            'gold': user.gold,
            'converted_gold': str(user.converted_gold),
            'total_wealth': str(user.wealth)
        }

        await channel_layer.group_send(
            f'wealth_{self.player_id}',
            {
                'type': 'send_wealth_update',
                'wealth': wealth_data
            }
        )
