from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('support', 'Support Team')
    ]
    # The user who is interacting with the bot/support team
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    # what was the message sent
    message = models.TextField()
    # message was sent by user, or bot or support
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    # when the message was sent
    timestamp = models.DateTimeField(auto_now_add=True)
    # whether user requested for support chat or not, default to False
    requested_for_support = models.BooleanField(default=False)
     # nullable field: if sender or receiver is support agent
    support_agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='support_chats',
        null=True,
        blank=True,
        help_text="Support agent involved in this chat (only if sender is support)"
    )

    def __str__(self):
        return f"{self.sender} - {self.user.username} at {self.timestamp}"
