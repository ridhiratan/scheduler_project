from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from events.models import Event
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Create 4 sample events: workshops, sports, literature, arts'

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(username='sample_creator', defaults={'email':'creator@example.com'})
        admin.set_password('password123')
        admin.save()

        now = timezone.now()
        samples = [
            ('Intro to Python', 'A hands-on workshop.', 'workshop', now + timedelta(days=3), now + timedelta(days=3, hours=2), 20),
            ('Inter-college Football', 'Open sports event.', 'sports', now + timedelta(days=5), now + timedelta(days=5, hours=3), 30),
            ('Poetry Evening', 'Literature reading', 'literature', now + timedelta(days=7), now + timedelta(days=7, hours=2), 50),
            ('Art & Craft Fair', 'Local arts and crafts', 'arts', now + timedelta(days=9), now + timedelta(days=9, hours=5), 100),
        ]
        for title, desc, cat, s, e, cap in samples:
            ev, created = Event.objects.get_or_create(title=title, defaults={
                'description': desc, 'category': cat, 'start_time': s, 'end_time': e,
                'capacity': cap, 'creator': admin
            })
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created {ev}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {ev}"))
