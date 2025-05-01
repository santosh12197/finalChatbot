from channels.generic.websocket import AsyncWebsocketConsumer
import json

class SupportChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'support_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', # triggers a method called chat_message()
                'message': message,
                'sender': self.scope['user'].username  # Assuming user is authenticated
            }
        )

    # Receive message from room group: Django sends the message back to clients
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket: Sends message back to all connected clients in that room using .send()
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
