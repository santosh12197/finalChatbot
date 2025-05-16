from django.db import models
from django.contrib.auth.models import User

# TODO : UserProfile
# class UserProfile(User):
#     pass

class ChatThread(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_threads')
    # support_agent = models.ForeignKey(
    #     User,
    #     on_delete=models.SET_NULL,
    #     related_name='assigned_threads',
    #     null=True,
    #     blank=True
    # )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # to track closed threads

    def __str__(self):
        return f"Thread with {self.user.username}" #(Support: {self.support_agent})"


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('support', 'Support Team')
    ]
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='chat_messages', null=True, blank=True)
    # The user who is interacting with the bot/support team
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_messages')
    # what was the message sent
    message = models.TextField()
    # message was sent by user, or bot or support
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    # when the message was sent
    timestamp = models.DateTimeField(auto_now_add=True)
    # whether user requested for support chat or not, default to False
    requested_for_support = models.BooleanField(default=False)
    # whether msg sent is read or not
    has_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
     # nullable field: if sender or receiver is support agent
    # support_agent = models.ForeignKey(
    #     User,
    #     on_delete=models.SET_NULL,
    #     related_name='support_chats',
    #     null=True,
    #     blank=True,
    #     help_text="Support agent involved in this chat (only if sender is support)"
    # )

    def __str__(self):
        return f"{self.sender} - {self.user.username} at {self.timestamp}"


class UserLocation(models.Model):
    # NOTE: model to Store User Location
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Location of {self.user.username}"