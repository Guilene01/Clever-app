from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.notes.models import Note


class Command(BaseCommand):
    help = "Seed a demo user and a few notes."

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(username="demo")
        if created:
            user.set_password("demo")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user (demo/demo)"))
        else:
            self.stdout.write("demo user already exists")

        sample_notes = [
            ("Grocery list", "milk, eggs, the entire produce section"),
            ("Standup notes", "yesterday: nothing\ntoday: meetings\nblockers: meetings"),
            ("Book ideas", "1. notes app\n2. notes app, but with AI"),
        ]
        for title, body in sample_notes:
            Note.objects.get_or_create(owner=user, title=title, defaults={"body": body})
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(sample_notes)} notes"))
