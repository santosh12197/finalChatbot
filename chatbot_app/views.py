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

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .utils import notify_support_of_unread, get_client_ip, get_location_from_ip, save_user_location

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


class ChatView(LoginRequiredMixin, View):
    """
        View for user's chatbot
    """
    def get(self, request):

        return render(
            request, 
            "chat.html"
        )
    
    def post(self, request):

        pass


@method_decorator(csrf_exempt, name='dispatch')
class MarkSupportRequestView(View):
    """
        View to mark support request by the user
    """
    def post(self, request):
        data = json.loads(request.body)
        user = request.user

        # get all the chat data for the user, and update requested_for_support as True
        ChatMessage.objects.filter(
            user=user, 
            # sender="user"
        ).update(
            requested_for_support=True,
            has_read=True
        )
        # ChatMessage.objects.create(
        #     user=user,
        #     message="User requested support",
        #     sender="user",
        #     requested_for_support=True,
        #     has_read=True
        # )
        return JsonResponse({"status": f"User {user} successfully marked as requested for support!"})


class CheckSupportChatView(LoginRequiredMixin, View):
    """
        This view checks if the current user already has support chat messages.
        If yes, it returns them along with a flag indicating the chat should be resumed.
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        # Check if support chat exists for the current user

        # Get the first interaction timestamp from the earliest message
        first_msg = ChatMessage.objects.filter(user=user, requested_for_support=True).order_by('timestamp').first()

        first_interaction_ist = None
        if first_msg and first_msg.first_interaction_timestamp:
            # Convert to IST for display
            first_interaction_ist = (first_msg.first_interaction_timestamp.astimezone(ZoneInfo("Asia/Kolkata"))).strftime('%d/%m/%Y %I:%M %p')


        # Find messages where requested_for_support is True
        support_messages = ChatMessage.objects.filter(user=user, requested_for_support=True).order_by('timestamp')

        if support_messages.exists():
            # Prepare the past messages as a list of dicts for frontend
            # Convert from utc to IST, since timestamp is stored in utc format in db
            messages = [
                {
                    'message': msg.message,
                    'sender': msg.sender,
                    'timestamp': (msg.timestamp.astimezone(ZoneInfo("Asia/Kolkata"))).strftime('%d/%m/%Y %I:%M %p'),
                }
                for msg in support_messages
            ]
    
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
        View to save chat msg
    """
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message')
        sender = data.get('sender')
        has_read = data.get('is_read')
        user_id = data.get('user_id')
        requested_for_support = data.get('requested_for_support', False)

        # Check if there is already a support chat message for this user
        existing_messages = ChatMessage.objects.filter(user=request.user, requested_for_support=True).order_by('timestamp')
        if not existing_messages.exists():
            # If this is the first support chat, set the first interaction timestamp
            first_interaction_timestamp = timezone.now()
        else:
            # Use the first interaction timestamp from the earliest message
            first_interaction_timestamp = existing_messages.first().first_interaction_timestamp

        if message and sender:
            # first save IP address of the user
            # save_user_location(request, request.user)
            # then save chat data of the user
            chat = ChatMessage.objects.create(
                user=request.user,
                message=message,
                sender=sender,
                requested_for_support=requested_for_support,
                has_read=has_read,
                first_interaction_timestamp=first_interaction_timestamp
            )

            # for updating user list on support dashboard
            # notify_support_of_unread(request.user.id)
            
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)


class MarkAsRead(LoginRequiredMixin, View):
    """
        View to update mark as read
    """
    def post(self, request, user_id):

        ChatMessage.objects.filter(
            user_id=user_id,
            sender='user',
            has_read=False
        ).update(has_read=True, read_at=timezone.now())

        return JsonResponse({'status': 'ok'})

class SupportDashboardView(LoginRequiredMixin, View):
    """
        Listing of users on support dashboard 
    """
    def dispatch(self, request, *args, **kwargs):
        """ 
            Check if the user is logged in and is a support agent, otherwise redirect to support login page
        """

        if not request.user.is_authenticated or not request.user.is_support_agent:
            return redirect('support_login')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        # Get users who requested support
        users = ChatMessage.objects.filter(
            sender='user',  
            requested_for_support=True
        ).values('user').distinct()

        user_ids = [u['user'] for u in users]

        # Subqueries to fetch latest message timestamp and message
        latest_msg_subquery = ChatMessage.objects.filter(
            user=OuterRef('pk'),
            sender='user',
            requested_for_support=True
        ).order_by('-timestamp')

        user_objs = UserProfile.objects.filter(id__in=user_ids).annotate(
            unread_count=Count(
                'user_messages',
                filter=Q(user_messages__sender='user', user_messages__has_read=False)
            ),
            latest_message=Subquery(latest_msg_subquery.values('message')[:1]),
            latest_timestamp=Subquery(latest_msg_subquery.values('timestamp')[:1])
        )

        ist = ZoneInfo("Asia/Kolkata")
        user_data = []

        for user in user_objs:
            try:
                loc = UserLocation.objects.get(user=user)
            except UserLocation.DoesNotExist:
                loc = None
            
            # Convert UTC to IST safely (only if timestamp exists)
            if user.latest_timestamp:
                ist_timestamp = user.latest_timestamp.astimezone(ist)
                formatted_timestamp = ist_timestamp.strftime('%d/%m/%Y %I:%M %p')
            else:
                formatted_timestamp = None

            user_data.append({
                "id": user.id,
                "username": user.username,
                "userEmail": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "lat": loc.latitude if loc else None,
                "lng": loc.longitude if loc else None,
                "latest_message": user.latest_message,
                "latest_timestamp": formatted_timestamp,
                "unread_count": user.unread_count,
            })

        context = {
            'users': user_data,
            # "user_data": user_data
        }
        template_name = 'support_dashboard.html'

        return render(request, template_name, context=context)
    

class GetChatHistoryView(View):
    """
        Chat history of a user
    """
    def get(self, request, user_id):
        chats = ChatMessage.objects.filter(user_id=user_id).order_by('timestamp')
        data = [
            {
                'sender': msg.sender,
                'message': msg.message,
                'timestamp': msg.timestamp.astimezone(ZoneInfo('Asia/Kolkata')).strftime("%d/%m/%Y %I:%M %p") # first convert timezone for UTC to IST timezone 
            }
            for msg in chats
        ]
        return JsonResponse(data, safe=False)
    

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
        user_id = data.get('user_id')
        support_id = data.get('support_member_id')

        if not user_id or not support_id:
            return JsonResponse({'status': 'error', 'message': 'Both user ID and support agent ID are required.'}, status=400)

        try:
            # Get the user thread
            user = UserProfile.objects.get(
                id=user_id,
                is_support_agent=False
            )
            if not user:
                return JsonResponse({'status': 'error', 'message': 'User does not exist for the given user ID.'}, status=404)

            support_agent = UserProfile.objects.get(
                id=support_id,
                is_support_agent=True
            )
            if not support_agent:
                return JsonResponse({'status': 'error', 'message': 'Support agent does not exist for the given support agent ID.'}, status=404)
            
            chat_thread = ChatThread.objects.get(
                user=user,
                is_active=True
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
                return JsonResponse({'status': 'success', "support_agent": support_agent.username, "user": user.username}, status=200)
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
                message="Welcome to SciPris. How can I help you?"
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
        user_id = request.GET.get("user_id")
        if not user_id:
            return JsonResponse({"error": "User ID required"}, status=400)
        
        try:
            chat_user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        
        # Ensure only support agents can access
        if not request.user.is_support_agent:
            return JsonResponse({"error": "Logged in user is not a support agent!"}, status=403)

        thread, created = ChatThread.objects.get_or_create(user=chat_user)

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

    # @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_support_agent:
            return JsonResponse({"error": "Logged in user is not a support agent!"}, status=403)

        data = json.loads(request.body)
        user_id = data.get("user_id")

        try:
            chat_user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        thread, _ = ChatThread.objects.get_or_create(user=chat_user)

        # Assign current support member
        thread.active_support_agent = request.user
        thread.support_agents.add(request.user)  # track involvement
        thread.save()

        return JsonResponse({"status": "assigned", "assigned_to": request.user.username})