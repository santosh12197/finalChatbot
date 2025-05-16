from django.contrib import admin
from .models import ChatMessage, UserLocation, ChatThread

# Register your models here.
admin.site.register(ChatMessage)
admin.site.register(UserLocation)
admin.site.register(ChatThread)