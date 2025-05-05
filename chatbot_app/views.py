from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import ChatMessage
from django.utils import timezone
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

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

        # Update the latest ChatMessage with requested_for_support=True
        ChatMessage.objects.create(
            user=user,
            message="User requested support",
            sender="user",
            requested_for_support=True
        )
        return JsonResponse({"status": "marked"})


class SaveChatMessageView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message')
        sender = data.get('sender')

        if message and sender:
            ChatMessage.objects.create(
                user=request.user,
                message=message,
                sender=sender
            )
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)


class SupportDashboardView(View):

    def get(self, request):
        # Get unique users who requested support
        users = ChatMessage.objects.filter(
            sender='user',  
            requested_for_support=True
        ).values('user').distinct()
        user_objs = User.objects.filter(id__in=[u['user'] for u in users])
        return render(request, 'support_dashboard.html', {'users': user_objs})
    

class GetChatHistoryView(View):

    def get(self, request, user_id):
        chats = ChatMessage.objects.filter(user_id=user_id).order_by('timestamp')
        data = [
            {
                'sender': msg.sender,
                'message': msg.message,
                'timestamp': msg.timestamp.strftime("%H:%M")
            }
            for msg in chats
        ]
        return JsonResponse(data, safe=False)