from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.ChatbotView.as_view(), name='chatbot'),
    path('satisfaction/', views.SatisfactionView.as_view(), name='satisfaction'),
    path('support_team/', views.SupportTeamView.as_view(), name='support_team'),
    path('support_chat/', views.SupportChatView.as_view(), name='support_chat'),
]
