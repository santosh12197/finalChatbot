from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/support/<str:room_name>/', consumers.SupportChatConsumer.as_asgi()),
]
