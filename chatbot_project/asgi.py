import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_project.settings')

django_asgi_app = get_asgi_application()

from .routing import application as channels_application  # Import project routing

from channels.routing import ProtocolTypeRouter

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": channels_application,   # <-- This handles WebSocket
})
