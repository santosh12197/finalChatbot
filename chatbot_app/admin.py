from django.contrib import admin
from .models import ChatMessage, UserLocation, ChatThread, UserProfile, PasswordResetOTP

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(ChatMessage)
admin.site.register(UserLocation)
admin.site.register(ChatThread)
admin.site.register(PasswordResetOTP)
