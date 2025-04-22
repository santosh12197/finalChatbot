from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sender = models.CharField(max_length=20, choices=[('bot', 'Bot'), ('user', 'User'), ('support', 'Support')])
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Chat message from {self.sender} at {self.timestamp}"

class SupportRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    connected_at = models.DateTimeField(null=True, blank=True)
    is_connected = models.BooleanField(default=False)

    def __str__(self):
        return f"Support request by {self.user.username} on {self.created_at}"

class SupportChat(models.Model):
    support_request = models.ForeignKey(SupportRequest, on_delete=models.CASCADE)
    message = models.TextField()
    sender = models.CharField(max_length=20, choices=[('user', 'User'), ('support', 'Support')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Support chat message from {self.sender} at {self.timestamp}"
