from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from todo.models import TodoItem


class Command(BaseCommand):
    help = "Email users about to-do items whose remind date has passed and haven't been reminded yet."

    def handle(self, *args, **options):
        due = TodoItem.objects.filter(
            completed=False,
            reminderSent=False,
            remindDate__isnull=False,
            remindDate__lte=timezone.now(),
        ).select_related('user')

        sent, skipped = 0, 0
        for item in due:
            if not item.user.email:
                self.stdout.write(self.style.WARNING(
                    f"Skipping '{item.title}' (id={item.pk}): user {item.user.username} has no email address"
                ))
                skipped += 1
                continue

            send_mail(
                subject=f"Reminder: {item.title}",
                message=(
                    f"Hi {item.user.username},\n\n"
                    f"This is a reminder for your to-do item \"{item.title}\", "
                    f"due {item.dueDate}.\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[item.user.email],
            )
            item.reminderSent = True
            item.save(update_fields=['reminderSent'])
            sent += 1

        self.stdout.write(self.style.SUCCESS(f"Sent {sent} reminder(s), skipped {skipped}."))
