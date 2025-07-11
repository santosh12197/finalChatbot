from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone



class UserProfile(AbstractUser):
    is_support_agent = models.BooleanField(default=False)
    # one doi (or article number)(for a particular user)
    # doi_or_article_number = models.CharField(max_length=255, null=True, blank=True) 
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "Personal Information"
        verbose_name_plural = "Personal Information"


class ChatThread(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_threads')
    # one doi (or article number) per thread (for a particular user)
    doi_or_article_number = models.CharField(max_length=255) 
    # Active support agent assigned to this thread, if any
    active_support_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='active_threads',
        null=True,
        blank=True
    )
    # Other support agents involved (view access, history)
    support_agents = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='involved_threads',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_closed = models.BooleanField(default=False)  # to track closed threads

    def __str__(self):
        return f"Thread with {self.user.username}" #(Support: {self.support_agent})"
    
    class Meta:
        verbose_name = "Chat Thread"
        verbose_name_plural = "Chat Thread"


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('support', 'Support Team')
    ]
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='chat_messages', null=True, blank=True)
    # The user who is interacting with the bot/support team
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_messages')
    # what was the message sent
    message = models.TextField()
    # message was sent by user, or bot or support
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    # when the message was sent
    timestamp = models.DateTimeField(auto_now_add=True)
    # whether user requested for support chat or not, default to False
    requested_for_support = models.BooleanField(default=False)
    # Field for tracking the first interaction timestamp in a support session
    first_interaction_timestamp = models.DateTimeField(null=True, blank=True)
    # whether msg sent is read or not
    has_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_active  = models.BooleanField(default=True) # Important: Make is_active=False when chat thread is closed
    # support agent involved in chat if any (if requested to chat with support team by the user): sender or receiver is support agent
    support_agent = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        related_name='support_chats',
        null=True,
        blank=True,
        help_text="Support agent involved in this chat (only when user has requested to chat with support)"
    )
    def __str__(self):
        return f"{self.sender} - {self.user.username} at {self.timestamp}"
    
    class Meta:
        verbose_name = "Chat Messages"
        verbose_name_plural = "Chat Messages"


class UserLocation(models.Model):
    # NOTE: model to Store User Location
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Location of {self.user.username}"
    
    class Meta:
        verbose_name = "User Location"
        verbose_name_plural = "User Location"


class PasswordResetOTP(models.Model):
    """
        Model to reset password 
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reset_otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.otp_code}"
    
    class Meta:
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTP"

    def is_expired(self):
        # 10 minutes expiry
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)