from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title


class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user} -> {self.event}"
