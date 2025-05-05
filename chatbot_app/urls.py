from django.urls import path
from .views import GetChatHistoryView, MarkSupportRequestView, RegisterView, LoginView, LogoutView, ChatView, SaveChatMessageView, SupportDashboardView

urlpatterns = [
    # login related
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # user related
    path("", ChatView.as_view(), name="chat"),
    path('mark_support_request/', MarkSupportRequestView.as_view(), name='mark_support_request'),
    path('save_message/', SaveChatMessageView.as_view(), name='save_message'),
    # support team related
    path('support_dashboard/', SupportDashboardView.as_view(), name='support_dashboard'),
    path('get_chat_history/<int:user_id>/', GetChatHistoryView.as_view(), name='get_chat_history'),
]
