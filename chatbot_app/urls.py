from django.urls import path
from .views import AssignSupportAgentView, CheckOrAssignSupportAgentView, CheckSupportChatView, CheckWelcomeMessagesView, CloseChatThreadView, GetAssignedSupportAndThreadIdView, GetChatHistoryView, MarkAsRead, MarkSupportRequestView, PasswordResetConfirmOTPView, PasswordResetRequestView, RegisterView, LoginView, LogoutView, ChatView, SaveChatMessageView, SciPrisIndexView, StartChatView, SupportDashboardView, SupportLoginView, SupportMembersListView, SupportRegisterView, ThreadListView, UserDetailsView, UserLocationView

urlpatterns = [

    # normal user login
    path('start_chat/', StartChatView.as_view(), name='start_chat'),
    path("user_details/", UserDetailsView.as_view(), name="user_details"),

    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", ChatView.as_view(), name="chat"),
    path('mark_support_request/', MarkSupportRequestView.as_view(), name='mark_support_request'),
    path('check_support_chat/', CheckSupportChatView.as_view(), name='check_support_chat'),
    path('save_message/', SaveChatMessageView.as_view(), name='save_message'),
    path('mark_as_read/<int:chat_thread_id>/', MarkAsRead.as_view(), name='mark_as_read'),
    path('close_chat_thread/<int:chat_thread_id>/', CloseChatThreadView.as_view(), name='mark_as_read'),

    # support team
    path("support_register/", SupportRegisterView.as_view(), name="support_register"),
    path("support_login/", SupportLoginView.as_view(), name="support_login"),
    path('support_dashboard/', SupportDashboardView.as_view(), name='support_dashboard'),
    path('get_chat_history/<int:chat_thread_id>/', GetChatHistoryView.as_view(), name='get_chat_history'),
    path('user_location/<int:user_id>/', UserLocationView.as_view(), name='user_location'),
    path('support_members/', SupportMembersListView.as_view(), name='support_members'),
    path('assign_support_member/', AssignSupportAgentView.as_view(), name='assign_support_member'),
    path("has_welcome_messages/", CheckWelcomeMessagesView.as_view(), name="has_welcome_messages"),
    path('check_or_assign_support/', CheckOrAssignSupportAgentView.as_view(), name='check_or_assign_support'),
    path('assigned_support_and_thread_id/', GetAssignedSupportAndThreadIdView.as_view(), name='assigned_support_and_thread_id'),
    path('chat_history/', ThreadListView.as_view(), name='chat_history'),

    # SciPris index page to integrate ChatBot
    path('index/', SciPrisIndexView.as_view(), name='index'),

    # forget password
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password_reset_confirm/', PasswordResetConfirmOTPView.as_view(), name='password_reset_confirm'),

]
