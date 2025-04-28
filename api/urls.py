from django.urls import path
from .views import ActiveChatsView

urlpatterns = [
    path('active_chats/', ActiveChatsView.as_view(), name='active_chats'),
]




