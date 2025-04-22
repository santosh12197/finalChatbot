from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Chat, SupportRequest, SupportChat
from datetime import datetime

class ChatbotView(View):
    def get(self, request):
        print("index")
        return render(request, 'chatbot.html', {'options': ['Payment Failure', 'Refund Issues', 'Invoice Requests', 'Other Payment Queries']})

    def post(self, request):
        print("Inside post")
        message = request.POST.get('message')
        print(message, "message")
        selected_option = request.POST.get('selected_option')

        if message == 'Hi! How can I help you today?':
            return JsonResponse({'message': 'How can I help you today?', 'options': ['Payment Failure', 'Refund Issues', 'Invoice Requests', 'Other Payment Queries']})

        # Handle button-based selections and send sub-options
        sub_options = self.get_sub_options(selected_option)
        return JsonResponse({'message': f"You selected: {selected_option}", 'sub_options': sub_options})

    def get_sub_options(self, selected_option):
        sub_options = {
            'Payment Failure': ['Card Payment Failure', 'Bank Transfer Failure'],
            'Refund Issues': ['Refund Status', 'Refund Delay', 'Refund Request'],
            'Invoice Requests': ['Invoice Not Received', 'Incorrect Invoice'],
            'Other Payment Queries': ['General Payment Inquiry', 'Payer Change/Modification', 'Payment Method Inquiry', 
                                      'Membership/Account Inquiry', 'Hold Payment Request', 'License/Billing Info',
                                      'Installments/Discount', 'Waiver/Other Issues', 'Signed Document Request', 'Payment Receipt Request']
        }
        return sub_options.get(selected_option, [])

class SatisfactionView(View):
    def post(self, request):
        satisfaction_response = request.POST.get('satisfaction_response')
        if satisfaction_response == 'Yes, I am satisfied':
            return JsonResponse({'message': "Thank you for connecting with SciPris Aptara."})
        elif satisfaction_response == 'No, Connect with Support Team':
            # Create a support request and connect with support
            support_request = SupportRequest.objects.create(user=request.user)
            return JsonResponse({'message': "Connecting with the support team."})

class SupportTeamView(View):
    def get(self, request):
        support_requests = SupportRequest.objects.filter(is_connected=False)
        return render(request, 'support_team.html', {'support_requests': support_requests})

    def post(self, request):
        support_request_id = request.POST.get('support_request_id')
        support_request = SupportRequest.objects.get(id=support_request_id)
        support_request.is_connected = True
        support_request.connected_at = datetime.now()
        support_request.save()

        return JsonResponse({'message': "Connected with support team."})

class SupportChatView(View):
    def post(self, request):
        support_request_id = request.POST.get('support_request_id')
        message = request.POST.get('message')

        support_request = SupportRequest.objects.get(id=support_request_id)
        SupportChat.objects.create(support_request=support_request, message=message, sender='support')

        return JsonResponse({'message': "Message sent to user."})
