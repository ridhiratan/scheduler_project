from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Event(models.Model):
    CATEGORY_WORKSHOP = 'workshop'
    CATEGORY_SPORTS = 'sports'
    CATEGORY_LITERATURE = 'literature'
    CATEGORY_ARTS = 'arts'
    CATEGORY_CHOICES = [
        (CATEGORY_WORKSHOP, 'Workshop'),
        (CATEGORY_SPORTS, 'Sports'),
        (CATEGORY_LITERATURE, 'Literature'),
        (CATEGORY_ARTS, 'Arts'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)

    def available_slots(self):
        # count only active (not cancelled)
        return self.capacity - self.reservations.filter(cancelled=False).count()

    def __str__(self):
        return f"{self.title} ({self.category})"

class Reservation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'user')  # prevents duplicate reservation

    def __str__(self):
        return f"{self.user} -> {self.event.title}"
