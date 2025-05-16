from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/support/<str:room_name>/', consumers.SupportChatConsumer.as_asgi()), # for chat of user with the support team
    path(r'ws/support_notifications/', consumers.SupportNotificationConsumer.as_asgi()), # list of users requested to chat with support team in real time 
]
