from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.db.models import Count
import json
from zoneinfo import ZoneInfo

from .models import ChatMessage, ChatThread
User = get_user_model()


class SupportChatConsumer(AsyncWebsocketConsumer):
    """
        Django Channels Group for chatting user with the support team with threaded chat handling
    """
    async def connect(self):
        self.user = self.scope["user"]
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
        sender = data["sender"] # 'user' or 'support'
        user_id = data.get('user_id')  # to identify user if sent from support
        # support_agent_username = data.get('support_agent')  # optional

        user = await self.get_user_by_userId(user_id)
        # support_agent = await self.get_user_by_username(support_agent_username)

        # Get or create active thread of the user
        thread = await self.get_or_create_active_thread(user)
        
        # Save message to DB
        chat = await self.save_message(thread, user, message, sender)#, support_agent)
        
        # Convert from utc to IST, since timestamp is stored in utc format in db
        chat_time_ist = chat.timestamp.astimezone(ZoneInfo("Asia/Kolkata"))
        # Format as desired
        timestamp = chat_time_ist.strftime('%d/%m/%Y %I:%M %p')

        # Broadcast message to all clients in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', # triggers a method called chat_message()
                'message': message,
                'sender': sender,  # Assuming user is authenticated
                'username': user.username,
                'timestamp': timestamp
            }
        )

        # Notify, this msg as unread, to support dashboard if the message is from user
        if sender == 'user':
            # support_msg_count = await database_sync_to_async(ChatMessage.objects.filter(
            #     user=chat.user,
            #     requested_for_support=True
            # ).count)()
            # print("support_msg_count: ", support_msg_count)

            # Get unread message count from this user
            unread_count = await self.get_unread_msg_count(user, thread)
            
            # Check if it's a new support thread (first support message from user)
            # if support_msg_count == 1:

            # new msg from user to support
            await self.channel_layer.group_send(
                'support_notifications',
                {
                    'type': 'new_support_thread',
                    'user': {
                        'id': chat.user.id,
                        'username': chat.user.username,
                        'first_name': chat.user.first_name,
                        'last_name': chat.user.last_name,
                        'email': chat.user.email,
                        'mobile': getattr(chat.user, 'mobile', ''),
                        'lat': getattr(chat.user, 'lat', ''),
                        'lng': getattr(chat.user, 'lng', ''),
                        "unread_count": unread_count,
                        "timestamp": timestamp,
                        "message": message,
                    }
                }
            )
            # else:
            #     await self.channel_layer.group_send(
            #         'support_notifications',
            #         {
            #             'type': 'send_unread_update',
            #             'user_id': user.id,
            #             'username': user.username,
            #             "message": message, 
            #             "unread_count": unread_count
            #         }
            #     )

    # Receive message from room group: Django sends the message back to clients
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        username = event['username']
        timestamp = event['timestamp']

        # Send message to WebSocket: Sends message back to all connected clients in that room using .send()
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'username': username,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def get_unread_msg_count(self, user, thread) :
        unread_count = ChatMessage.objects.filter(
            thread=thread,
            thread__is_active=True,
            user=user,
            sender='user',
            has_read=False
        ).count()
        return unread_count
    
    # TODO : to see: sender = bot, when user sends msg (but it should be user) -------------------------------
    @database_sync_to_async
    def get_user_by_userId(self, user_id):
        user = User.objects.get(id=user_id)
        # sender = ChatMessage.objects.filter(user=user).last().sender
        return user

    @database_sync_to_async
    def get_or_create_active_thread(self, user):
        # Get active thread if any, else create new
        thread = ChatThread.objects.filter(user=user, is_active=True).first()
        if thread:
            return thread
        return ChatThread.objects.create(user=user) 
    
    @database_sync_to_async
    def save_message(self, thread, user, message, sender):#, support_agent):
        chat = ChatMessage.objects.create(
            thread=thread,
            user=user,
            message=message,
            sender=sender,
            has_read=False,
            requested_for_support=True,  
            # support_agent=support_agent if sender == 'support' else None
        )
        return chat


class SupportNotificationConsumer(AsyncWebsocketConsumer):
    """
        Notifies support team for new chat threads or unread messages.
    """

    async def connect(self):
        self.group_name = 'support_notifications'

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Called when a new msg is sent from the user to the support
    async def new_support_thread(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_support_thread',
            'user': event['user'],  # dict with id, username, etc.
        }))

    # Called when an unread message arrives in an existing thread
    # async def send_unread_update(self, event):
    #     print("unread event: ", event)
    #     await self.send(text_data=json.dumps({
    #         'type': 'unread_message',
    #         'user_id': event['user_id'],
    #         'message': event.get('message', ''),
    #         'unread_count': event.get('unread_count', 1)  # default to 1 if not present
    #     }))
