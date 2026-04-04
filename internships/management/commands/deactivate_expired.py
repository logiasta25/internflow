from django.core.management.base import BaseCommand
from django.utils import timezone
from internships.models import Internship

class Command(BaseCommand):
    help = 'Deactivate internships past their last application date'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        expired = Internship.objects.filter(last_date__lt=today, is_active=True)
        count = expired.update(is_active=False)
        self.stdout.write(self.style.SUCCESS(f"Successfully deactivated {count} expired internship(s)."))
