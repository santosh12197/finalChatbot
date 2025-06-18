from django.db.models import Count, Q, OuterRef, Subquery
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import requests

from .models import ChatMessage, ChatThread, UserLocation, UserProfile
from django.utils import timezone
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from zoneinfo import ZoneInfo
from django.contrib.auth.hashers import make_password

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .utils import notify_support_of_unread, get_client_ip, get_location_from_ip, save_user_location, iframe_exempt

INITIAL_OPTIONS = [
    "Payment Failure",
    "Refund Issues",
    "Invoice Requests",
    "Other Payment Queries"
]

SUB_OPTIONS = {
    "Payment Failure": ["Card Payment Failure", "Bank Transfer Failure"],
    "Refund Issues": ["Refund Status", "Refund Delay", "Refund Request"],
    "Invoice Requests": ["Invoice Not Received", "Incorrect Invoice"],
    "Other Payment Queries": [
        "General Payment Inquiry", "Payer Change/Modification", "Payment Method Inquiry",
        "Membership/Account Inquiry", "Hold Payment Request", "License / Billing Info",
        "Installments/Discount", "Waiver/Other Issues", "Signed Document Request",
        "Payment Receipt Request"
    ]
}


class StartChatView(View):
    """ 
        - Each time, user clicks on start chat after entering name, email, doi, then first register then login that user:
            - each time, first close all the other active chat threads of that user, and then create a new chat thread with user and doi.
            - each thread is chat session wise.
    """
    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        doi = request.POST.get("doi")
        # query = request.POST.get("query")

        if not all([name, email, doi]):
            return JsonResponse({"success": False, "error": "All fields are required."}, status=400)
        
        # Split full name into first and last name
        name_parts = name.strip().split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Get or create user
        user, created = UserProfile.objects.get_or_create(
            username=email,
            email=email,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'password': make_password('start@123')
            }
        )

        # Log user in
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)

        # TODO: May think later to re-use the active chat threads of the user
        
        # For now, close all the active threads of the user, and
        # create a new thread for user with the doi
        ChatThread.objects.filter(
            user=user, 
            is_closed=False
        ).update(is_closed=True)

        thread = ChatThread.objects.create(
            user=user, 
            doi_or_article_number=doi
        )

        # Redirect to chat interface
        # return redirect("chat")  # This resolves to `path("", ChatView.as_view(), name="chat")`
        return JsonResponse({"success": True, "thread_id": thread.id})

class RegisterView(View):
    """
        Registration view for normal user
    """
    def get(self, request):
        return render(request, "register.html")
    
    def post(self, request):
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Basic field validation
        if not all([first_name, email, password]):
            messages.error(request, "first_name, email and password are required.")
            return render(request, self.template_name)

        # Check for unique email
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, f"Email {email} is already registered.")
            return render(request, self.template_name)

        # Create user
        user = UserProfile.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_support_agent=False
        )
        user.save()

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')  
    
@iframe_exempt
class UserDetailsView(View):

    def get(self, request):
        return render(request, "user_details.html") 


class LoginView(View):
    """
        Login view for normal user
    """
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        email = request.POST["email"]
        password = request.POST["password"]
        
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("chat")
        
        return render(request, "login.html", {"error": "Invalid credentials"})


class LogoutView(View):
    """
        Logout view for normal user and support agent
    """
    def post(self, request):

         # Check if the current user is a support agent **before** logging out
        is_support_agent = getattr(request.user, 'is_support_agent', False)
        
        # Now, log the user out
        logout(request)
        
        # Redirect based on the stored value
        if is_support_agent:
            return redirect("support_login")
        else:
            return redirect("login")


class SupportRegisterView(View):
    """
        Registration view for support agent
    """
    template_name = 'support_register.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Basic field validation
        if not all([first_name, email, password]):
            messages.error(request, "first_name, email and password are required.")
            return render(request, self.template_name)

        # Email domain validation
        # if not email.endswith('@aptaracorp.com'):
        #     messages.error(request, "Email must be from @aptaracorp.com domain.")
        #     return render(request, self.template_name)

        # Check for unique email
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, f"Email {email} is already registered.")
            return render(request, self.template_name)

        # Password length check
        # if len(password) < 8:
        #     messages.error(request, "Password must be at least 8 characters long.")
        #     return render(request, self.template_name)

        # Create user
        user = UserProfile.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_support_agent=True
        )
        user.save()

        messages.success(request, "Registration successful! Please login.")
        return redirect('support_login')  
    

class SupportLoginView(View):
    """
        Login view for support agent
    """
    template_name = 'support_login.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Basic field validation
        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return render(request, self.template_name)

        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)

        if user is not None and user.is_support_agent:
            login(request, user)
            # messages.success(request, f"Welcome, {user.first_name}!")
            return redirect('support_dashboard')  # redirect to support_dashboard page after login
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, self.template_name)


@iframe_exempt
class ChatView(LoginRequiredMixin, View):
    """
        View for user's chatbot
    """
    def get(self, request):

        return render(
            request, 
            "chat.html"
        )


# @method_decorator(csrf_exempt, name='dispatch')
class MarkSupportRequestView(View):
    """
        View to mark support request by the user
    """
    def post(self, request):
        data = json.loads(request.body)
        user = request.user
        chat_thread_id = data["chat_thread_id"]
        # get all the chat data for the chat trhread id, and update requested_for_support as True
        if not chat_thread_id:
            return JsonResponse({"status": "Error"})
        
        chat_thread = ChatThread.objects.filter(id=chat_thread_id).first()
        if not chat_thread:
            return JsonResponse({"status": "No chat thread"})
        
        ChatMessage.objects.filter(
            thread=chat_thread, 
            thread__is_closed=False
        ).update(
            requested_for_support=True,
            has_read=True,
        )
        return JsonResponse({"status": f"User {user} successfully marked as requested for support!"})


class CheckSupportChatView(LoginRequiredMixin, View):
    """
        This view checks if the current user already has support chat messages.
        If yes, it returns them along with a flag indicating the chat should be resumed on user side.
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        # Check if support chat exists for the current user

        # Get the first interaction timestamp from the earliest message
        first_msg = ChatMessage.objects.filter(
            user=user, 
            requested_for_support=True,
            is_active=True,
            # thread__is_closed=False,
        ).order_by('timestamp').first()

        first_interaction_ist = None
        if first_msg and first_msg.first_interaction_timestamp:
            # Convert to IST for display
            first_interaction_ist = (first_msg.first_interaction_timestamp.astimezone(ZoneInfo("Asia/Kolkata"))).strftime('%d/%m/%Y %I:%M %p')


        # Find messages where requested_for_support is True
        support_messages = ChatMessage.objects.filter(
            user=user, 
            requested_for_support=True,
            is_active=True,
            # thread__is_closed=False,
        ).order_by('timestamp')

        if support_messages.exists():
            messages = []
            for msg in support_messages:
                # Default values
                support_full_name = ""
                if msg.support_agent:
                    first_name = msg.support_agent.first_name or ""
                    last_name = msg.support_agent.last_name or ""
                    support_full_name = f"{first_name} {last_name}".strip()

                # Safe timestamp conversion
                timestamp = ""
                if msg.timestamp:
                    try:
                        timestamp = msg.timestamp.astimezone(ZoneInfo("Asia/Kolkata")).strftime('%d/%m/%Y %I:%M %p')
                    except Exception as e:
                        timestamp = "Invalid Time"

                messages.append({
                    'message': msg.message,
                    'sender': msg.sender,
                    'support_full_name': support_full_name,
                    'timestamp': timestamp,
                })
    
            return JsonResponse({
                'support_chat_exists': True,
                'messages': messages,
                'first_interaction_timestamp': first_interaction_ist,
            })
        else:
            # No support chat, start with the botTree flow
            return JsonResponse({'support_chat_exists': False})


class SaveChatMessageView(LoginRequiredMixin, View):
    """
        View to save chat msg:
        - when user starts chat with bot, then create or retrieve active chat thread of user and save chat in that thread.
        - user chat is tracked through this actice chat thread unless it is closed by user or support agent.
    """
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message')
        sender = data.get('sender')
        has_read = data.get('is_read')
        user_id = data.get('user_id')
        support_agent_id = data.get('support_agent_id')
        requested_for_support = data.get('requested_for_support', False)

        if not (message and sender and user_id):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

        user = UserProfile.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        support_agent = UserProfile.objects.filter(id=support_agent_id).first() if support_agent_id else None

        # Get or create an active ChatThread
        thread = ChatThread.objects.filter(
            user=user, 
            is_closed=False
        ).first()

        if not thread:
            thread = ChatThread.objects.create(
                user=user, 
                active_support_agent=support_agent
            )
            if support_agent:
                thread.support_agents.add(support_agent)


        # Check if there is already a support chat message for this user
        existing_messages = ChatMessage.objects.filter(user=request.user, requested_for_support=True).order_by('timestamp')
        if not existing_messages.exists():
            # If this is the first support chat, set the first interaction timestamp
            first_interaction_timestamp = timezone.now()
        else:
            # Use the first interaction timestamp from the earliest message
            first_interaction_timestamp = existing_messages.first().first_interaction_timestamp

        # Create the ChatMessage
        ChatMessage.objects.create(
            thread=thread,
            user=user,
            support_agent=support_agent,
            message=message,
            sender=sender,
            requested_for_support=requested_for_support,
            has_read=has_read,
            first_interaction_timestamp=first_interaction_timestamp,
        )

            # for updating user list on support dashboard
            # notify_support_of_unread(request.user.id)
            
        return JsonResponse({'status': 'success'})


class MarkAsRead(LoginRequiredMixin, View):
    """
        View to update mark as read
    """
    def post(self, request, chat_thread_id):

        ChatMessage.objects.filter(
            thread__id=chat_thread_id,
            thread__is_closed=False,
            has_read=False
        ).update(has_read=True, read_at=timezone.now())

        return JsonResponse({'status': 'ok'})

# class SupportDashboardView(LoginRequiredMixin, View):
#     """
#         Listing of users on support dashboard 
#     """
#     def dispatch(self, request, *args, **kwargs):
#         """ 
#             Check if the user is logged in and is a support agent, otherwise redirect to support login page
#         """

#         if not request.user.is_authenticated or not request.user.is_support_agent:
#             return redirect('support_login')
#         return super().dispatch(request, *args, **kwargs)
    
#     def get(self, request):
#         # Get users who requested support
#         users = ChatMessage.objects.filter(
#             sender='user',  
#             requested_for_support=True
#         ).values('user').distinct()

#         user_ids = [u['user'] for u in users]

#         # Subqueries to fetch latest message timestamp and message
#         latest_msg_subquery = ChatMessage.objects.filter(
#             user=OuterRef('pk'),
#             sender='user',
#             requested_for_support=True
#         ).order_by('-timestamp')

#         user_objs = UserProfile.objects.filter(id__in=user_ids).annotate(
#             unread_count=Count(
#                 'user_messages',
#                 filter=Q(user_messages__sender='user', user_messages__has_read=False)
#             ),
#             latest_message=Subquery(latest_msg_subquery.values('message')[:1]),
#             latest_timestamp=Subquery(latest_msg_subquery.values('timestamp')[:1])
#         )

#         ist = ZoneInfo("Asia/Kolkata")
#         user_data = []

#         for user in user_objs:
#             try:
#                 loc = UserLocation.objects.get(user=user)
#             except UserLocation.DoesNotExist:
#                 loc = None
            
#             # Convert UTC to IST safely (only if timestamp exists)
#             if user.latest_timestamp:
#                 ist_timestamp = user.latest_timestamp.astimezone(ist)
#                 formatted_timestamp = ist_timestamp.strftime('%d/%m/%Y %I:%M %p')
#             else:
#                 formatted_timestamp = None

#             user_data.append({
#                 "id": user.id,
#                 "username": user.username,
#                 "userEmail": user.email,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "lat": loc.latitude if loc else None,
#                 "lng": loc.longitude if loc else None,
#                 "latest_message": user.latest_message,
#                 "latest_timestamp": formatted_timestamp,
#                 "unread_count": user.unread_count,
#             })

#         context = {
#             'users': user_data,
#             # "user_data": user_data
#         }
#         template_name = 'support_dashboard.html'

#         return render(request, template_name, context=context)


  
class SupportDashboardView(LoginRequiredMixin, View):
    """
    Display all chat threads (active or closed) requested for support.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_support_agent:
            return redirect('support_login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Get all active threads where at least one message requested support
        threads = ChatThread.objects.filter(
            chat_messages__requested_for_support=True,
            is_closed=False,
        ).distinct().prefetch_related(
            'user'
        ).annotate(
            unread_count=Count(
                'chat_messages',
                filter=Q(chat_messages__sender='user', chat_messages__has_read=False)
            )
        )

        # Subquery: latest message content & timestamp (from user)
        latest_msg_subquery = ChatMessage.objects.filter(
            thread=OuterRef('pk'),
            sender='user'
        ).order_by('-timestamp')

        threads = threads.annotate(
            latest_message=Subquery(latest_msg_subquery.values('message')[:1]),
            latest_timestamp=Subquery(latest_msg_subquery.values('timestamp')[:1])
        )

        ist = ZoneInfo("Asia/Kolkata")
        thread_data = []

        for thread in threads:
            user = thread.user
            try:
                loc = UserLocation.objects.get(user=user)
            except UserLocation.DoesNotExist:
                loc = None

            formatted_timestamp = None
            if thread.latest_timestamp:
                formatted_timestamp = thread.latest_timestamp.astimezone(ist).strftime('%d/%m/%Y %I:%M %p')

            thread_data.append({
                'thread_id': thread.id,
                'user_id': user.id,
                'username': user.username,
                'userEmail': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'lat': loc.latitude if loc else None,
                'lng': loc.longitude if loc else None,
                'latest_message': thread.latest_message,
                'latest_timestamp': formatted_timestamp,
                'unread_count': thread.unread_count,
                'is_closed': thread.is_closed,
            })

        context = {
            'threads': thread_data
        }

        return render(request, 'support_dashboard.html', context)  

class GetChatHistoryView(View):
    """
        Chat history of a user
    """
    def get(self, request, chat_thread_id):

        chat_thread = ChatThread.objects.filter(id=chat_thread_id).first()
        if not chat_thread:
            return JsonResponse({
                "Error": "Chat thread does not exist!",
                'support_chat_exists': False,
                'messages': [],
                'first_interaction_timestamp': None,
            })
        
        # Get the first interaction timestamp from the earliest message
        first_msg = ChatMessage.objects.filter(
            user=chat_thread.user, 
            requested_for_support=True,
            is_active=True,
        ).order_by('timestamp').first()

        first_interaction_ist = None
        if first_msg and first_msg.first_interaction_timestamp:
            # Convert to IST for display
            first_interaction_ist = (first_msg.first_interaction_timestamp.astimezone(ZoneInfo("Asia/Kolkata"))).strftime('%d/%m/%Y %I:%M %p')

        chats = ChatMessage.objects.filter(
            user=chat_thread.user,
            requested_for_support=True,
            is_active=True,
        ).order_by('timestamp')

        if chats.exists():
            messages = []
            for msg in chats:

                # Default values of support agent of a particular chat
                support_full_name = ""
                support_agent_id = None
                if msg.support_agent:
                    first_name = msg.support_agent.first_name or ""
                    last_name = msg.support_agent.last_name or ""
                    support_full_name = f"{first_name} {last_name}".strip()
                    support_agent_id = msg.support_agent.id
                
                # Safe timestamp conversion
                timestamp = ""
                if msg.timestamp:
                    try:
                        timestamp = msg.timestamp.astimezone(ZoneInfo("Asia/Kolkata")).strftime('%d/%m/%Y %I:%M %p')
                    except Exception as e:
                        timestamp = "Invalid Time"

                messages.append({
                    'message': msg.message,
                    'sender': msg.sender,
                    "support_agent_id": support_agent_id,
                    "support_full_name": support_full_name,
                    'timestamp': timestamp,
                })

            return JsonResponse({
                'support_chat_exists': True,
                'messages': messages,
                'first_interaction_timestamp': first_interaction_ist,
            })

        return JsonResponse({
            'support_chat_exists': False,
            'messages': [],
            'first_interaction_timestamp': None,
        })
    

class UserLocationView(View):
    """
        User location based on IP address
    """
    def get(self, request, user_id):
        try:
            user = UserProfile.objects.get(id=user_id)

            # Get the most recent IP address from ChatMessage, or default
            last_message = UserLocation.objects.filter(user=user).order_by('-updated_at').first()
            ip = request.META.get('REMOTE_ADDR') if last_message is None else last_message.ip_address # TODO : update IP dynamically using get_client_ip() inside utils.py

            # Use IP Geolocation API
            response = requests.get(f"http://ip-api.com/json/8.8.8.8") # TODO :to replace 8.8.8.8 by {ip}
            data = response.json()
            if data['status'] == 'success':
                return JsonResponse({
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'city': data['city'],
                    'country': data['country'],
                })
            else:
                return JsonResponse({'error': 'Could not fetch location'}, status=400)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        

class SupportMembersListView(LoginRequiredMixin, View):
    """
        List all support members except the current logged-in agent.
    """
    def get(self, request, *args, **kwargs):
        current_support_agent = request.user
        # Filter only support agents except the current user
        support_agents = UserProfile.objects.filter(
            is_support_agent=True
        ).exclude(id=current_support_agent.id)

        data = [
            {
                "id": agent.id,
                "first_name": agent.first_name,
                "last_name": agent.last_name,
                "username": agent.username
            }
            for agent in support_agents
        ]

        return JsonResponse({"support_agents": data})
    

class AssignSupportAgentView(View):
    """
        - Assigning support agent to a user's chat thread
        - Assigning of user to support agent should be done only when:
            (1) current user for chat thread is not assigned to any support agent -> that can be done by any support agent
            (2) if already assigned, then the assignment can be done only by the support agent who has been assigned to the user
    """
    def post(self, request):
        # only support agent can assign
        if not request.user.is_support_agent:
            return JsonResponse({'status': 'error', 'message': 'Only support agents can assign users.'}, status=403)

        data = json.loads(request.body)
        chat_thread_id = data.get('chat_thread_id')
        support_id = data.get('support_member_id')

        if not chat_thread_id or not support_id:
            return JsonResponse({'status': 'error', 'message': 'Both chat thread ID and support agent ID are required.'}, status=400)

        try:
            # support validation
            support_agent = UserProfile.objects.get(
                id=support_id,
                is_support_agent=True
            )
            if not support_agent:
                return JsonResponse({'status': 'error', 'message': 'Support agent does not exist for the given support agent ID.'}, status=404)
            
            # chat thread validation
            chat_thread = ChatThread.objects.get(
                id=chat_thread_id,
                is_closed=False,
            )
            if not chat_thread:
                return JsonResponse({'status': 'error', 'message': 'Active chat thread does not exist for the given user.'}, status=404)

            # assigning support agent validation
            if not chat_thread.active_support_agent and request.user != support_agent:
                return JsonResponse({'status': 'error', 'message': 'You can only assign user to yourself if user is not assigned to any support agent!'}, status=400)

            if not chat_thread.active_support_agent or (chat_thread.active_support_agent and chat_thread.active_support_agent == request.user):
                # Assign the support agent
                chat_thread.active_support_agent = support_agent
                chat_thread.support_agents.add(support_agent)  # add to involved agents if not already
                chat_thread.save()
                return JsonResponse({'status': 'success', "support_agent": support_agent.username, "user": chat_thread.user.username}, status=200)
            else:
                return JsonResponse({'status': 'error', 'message': 'User is already assigned to other support agent. You can not perform this operation.'}, status=400)
            
        except Exception as e:
            # print(e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        

class CheckWelcomeMessagesView(View):
    """
        Check for initial support msg, when user is connected with support team
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")

            success_exists = ChatMessage.objects.filter(
                user_id=user_id,
                sender="bot",
                message="Successfully connected with the support team."
            ).exists()

            welcome_exists = ChatMessage.objects.filter(
                user_id=user_id,
                sender="support",
                message="Welcome to Aptara. How can I help you?"
            ).exists()

            return JsonResponse({
                "success_sent": success_exists,
                "welcome_sent": welcome_exists,
                "both_sent": success_exists and welcome_exists
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        

class CheckOrAssignSupportAgentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        chat_thread_id = request.GET.get("chat_thread_id")
        if not chat_thread_id:
            return JsonResponse({"error": "Chat thread ID required!"}, status=400)
        
        # Ensure only support agents can access
        if not request.user.is_support_agent:
            return JsonResponse({"error": "Logged in user is not a support agent!"}, status=403)

        thread, created = ChatThread.objects.get_or_create(id=chat_thread_id)

        if thread.active_support_agent:
            if thread.active_support_agent == request.user:
                return JsonResponse({"status": "assigned_to_you"})
            else:
                return JsonResponse({
                    "status": "assigned_to_other",
                    "assigned_to": thread.active_support_agent.username
                })
        else:
            return JsonResponse({"status": "unassigned"})

    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_support_agent:
            return JsonResponse({"error": "Logged in user is not a support agent!"}, status=403)

        data = json.loads(request.body)
        chat_thread_id = data.get("chat_thread_id")
        
        if not chat_thread_id:
            return JsonResponse({"error": "Chat thread ID is required!"}, status=403)

        thread, _ = ChatThread.objects.get_or_create(id=chat_thread_id)

        # Assign current support member
        thread.active_support_agent = request.user
        thread.support_agents.add(request.user)  # track support agents involvement
        thread.save()

        return JsonResponse({"status": "assigned", "assigned_to": request.user.username})
    

class GetAssignedSupportAndThreadIdView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            thread = ChatThread.objects.filter(
                user=request.user,
                is_closed=False
            ).first()
            if thread:
                if thread.active_support_agent:
                    return JsonResponse({
                        'status': 'success',
                        'thread_id': thread.id,
                        'support_agent_id': thread.active_support_agent.id,
                        'support_agent_name': f"{thread.active_support_agent.first_name} {thread.active_support_agent.last_name}"
                    })
                else:
                    return JsonResponse({
                        'status': 'no_active_support_on_thread',
                        'thread_id': thread.id,
                        'support_agent_id': None,
                        'support_agent_name': None
                    })
            else:
                return JsonResponse({
                    'status': 'no_active_thread',
                    'thread_id': None,
                    'support_agent_id': None,
                    'support_agent_name': None
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


class CloseChatThreadView(View):
    def post(self, request, chat_thread_id):
        try:
            thread = ChatThread.objects.filter(
                id=chat_thread_id,
                is_closed=False
            ).order_by("-created_at").first()

            data = json.loads(request.body)
            support_agent_id = data.get('support_agent_id') # support agent id who is requesting to close the chat

            if not thread:
                return JsonResponse({'success': False, 'error': 'No active chat thread found!', 'message': 'no_active_thread'})

            # only assigned support agent (currently active support agent)/ user should close the chat
            # user validation
            if not request.user.is_support_agent:
                if request.user != thread.user:
                    return JsonResponse({'success': False, 'error': f'Not a valid user to close the chat with user {thread.user.first_name} {thread.user.last_name}!'})
            # support agent validation
            # if chat thread is assigned to any support, then, active support of the chat thread should be the support member who is requesting to close the chat.
            # or, if chat thread is not assigned to any support, then any support member can close the chat.
            if support_agent_id:
                if thread.active_support_agent:
                    if int(thread.active_support_agent.id) != int(support_agent_id):
                        return JsonResponse({'success': False, 'error': f'User {thread.user.first_name} {thread.user.last_name} has been assigned with support member {thread.active_support_agent.first_name} {thread.active_support_agent.last_name}. You can not close the chat for current user!'})

            # close the thread
            thread.is_closed = True
            thread.save()

            # Broadcast a “chat closed” event from the view
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"support_{thread.id}",  # Same as room_group_name in consumer
                {
                    "type": "chat_close_notify",  # Triggers `chat_close_notify` method in consumer
                    "message": "This chat has been closed.",
                    "thread_id": thread.id,
                    "user_id": thread.user.id,
                    "user_name": f"{thread.user.first_name} {thread.user.last_name}",
                }
            )

            # Mark all messages in this thread as inactive msg
            ChatMessage.objects.filter(thread=thread).update(
                is_active=False,
            )

            return JsonResponse({'success': True, "message": "Thread closed successfully."})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        

class SciPrisIndexView(View):
    """
        Integrate ChatBot on SciPris index page
    """
    def get(self, request):
        # return render(request, 'scipris_index.html') 
        return render(request, 'scipris_login.html') 
    

class ThreadListView(View):
    """
        List of all the chat threads
    """
    def get(self, request):
        # TODO : doing here-------------
        # return render(request, 'scipris_index.html') 
        return render(request, 'thread_list.html') 
    
