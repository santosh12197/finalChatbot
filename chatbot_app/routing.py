from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/support/<str:room_name>/', consumers.SupportChatConsumer.as_asgi()), # for chat of user with the support team
    # path('ws/support/dashboard/', consumers.SupportDashboardConsumer.as_asgi()), # to notify the support team dashboard of new user requests in real time 
]
