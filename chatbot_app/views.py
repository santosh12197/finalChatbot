from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import ChatMessage
from django.utils import timezone
from datetime import date
from django.http import JsonResponse
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

