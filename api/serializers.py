from rest_framework import serializers

from chatbot_app.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessage
        fields = ("id", "user", "message", "sender", "timestamp", "support_agent")