from django.db.models import Count, Q, OuterRef, Subquery
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import requests

from .models import ChatMessage, UserLocation
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
    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already exists. Please choose another."
            })

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("chat")

class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("chat")
        
        return render(request, "login.html", {"error": "Invalid credentials"})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")

class ChatView(LoginRequiredMixin, View):

    def get(self, request):

        return render(
            request, 
            "chat.html"
        )
    
    def post(self, request):

        pass


@method_decorator(csrf_exempt, name='dispatch')
class MarkSupportRequestView(View):
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

    def post(self, request, user_id):

        ChatMessage.objects.filter(
            user_id=user_id,
            sender='user',
            has_read=False
        ).update(has_read=True, read_at=timezone.now())

        return JsonResponse({'status': 'ok'})

class SupportDashboardView(View):

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

        user_objs = User.objects.filter(id__in=user_ids).annotate(
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
            user = User.objects.get(id=user_id)

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
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)