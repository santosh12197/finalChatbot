from django.urls import path
from .views import AssignSupportAgentView, CheckOrAssignSupportAgentView, CheckSupportChatView, CheckWelcomeMessagesView, CloseChatThreadView, GetAssignedSupportAgentView, GetChatHistoryView, MarkAsRead, MarkSupportRequestView, RegisterView, LoginView, LogoutView, ChatView, SaveChatMessageView, SupportDashboardView, SupportLoginView, SupportMembersListView, SupportRegisterView, UserLocationView

urlpatterns = [
    # normal user login related
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # normal user related
    path("", ChatView.as_view(), name="chat"),
    path('mark_support_request/', MarkSupportRequestView.as_view(), name='mark_support_request'),
    path('check_support_chat/', CheckSupportChatView.as_view(), name='check_support_chat'),
    path('save_message/', SaveChatMessageView.as_view(), name='save_message'),
    path('mark_as_read/<int:user_id>/', MarkAsRead.as_view(), name='mark_as_read'),
    path('close_chat_thread/<int:user_id>/', CloseChatThreadView.as_view(), name='mark_as_read'),

    # support team related
    path("support_register/", SupportRegisterView.as_view(), name="support_register"),
    path("support_login/", SupportLoginView.as_view(), name="support_login"),
    path('support_dashboard/', SupportDashboardView.as_view(), name='support_dashboard'),
    path('get_chat_history/<int:user_id>/', GetChatHistoryView.as_view(), name='get_chat_history'),
    path('user_location/<int:user_id>/', UserLocationView.as_view(), name='user_location'),
    path('support_members/', SupportMembersListView.as_view(), name='support_members'),
    path('assign_support_member/', AssignSupportAgentView.as_view(), name='assign_support_member'),
    path("has_welcome_messages/", CheckWelcomeMessagesView.as_view(), name="has_welcome_messages"),
    path('check_or_assign_support/', CheckOrAssignSupportAgentView.as_view(), name='check_or_assign_support'),
    path('get_assigned_support_agent/', GetAssignedSupportAgentView.as_view(), name='get_assigned_support_agent'),
]
