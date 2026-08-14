from datetime import timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .models import TodoItem


class SendRemindersTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice', password='pw', email='alice@example.com'
        )

    def _make_item(self, **kwargs):
        defaults = {
            'user': self.user,
            'title': 'Test item',
            'dueDate': timezone.now() + timedelta(days=1),
            'remindDate': timezone.now() - timedelta(minutes=5),
        }
        defaults.update(kwargs)
        return TodoItem.objects.create(**defaults)

    def test_sends_email_for_due_reminder(self):
        item = self._make_item()

        call_command('send_reminders')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(item.title, mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['alice@example.com'])
        item.refresh_from_db()
        self.assertTrue(item.reminderSent)

    def test_does_not_resend(self):
        self._make_item(reminderSent=True)

        call_command('send_reminders')

        self.assertEqual(len(mail.outbox), 0)

    def test_skips_future_reminders(self):
        self._make_item(remindDate=timezone.now() + timedelta(days=1))

        call_command('send_reminders')

        self.assertEqual(len(mail.outbox), 0)

    def test_skips_completed_items(self):
        self._make_item(completed=True)

        call_command('send_reminders')

        self.assertEqual(len(mail.outbox), 0)

    def test_skips_user_without_email(self):
        userNoEmail = User.objects.create_user(username='bob', password='pw', email='')
        self._make_item(user=userNoEmail)

        call_command('send_reminders')

        self.assertEqual(len(mail.outbox), 0)

    def test_editing_remind_date_resets_reminder_sent(self):
        item = self._make_item(reminderSent=True)

        item.remindDate = timezone.now() - timedelta(minutes=1)
        item.save()

        item.refresh_from_db()
        self.assertFalse(item.reminderSent)


class TodoCheckboxToggleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='carol', password='pw')
        self.client.force_login(self.user)
        self.item = TodoItem.objects.create(
            user=self.user,
            title='Test item',
            dueDate=timezone.now() + timedelta(days=1),
            remindDate=timezone.now() + timedelta(hours=1),
        )

    def test_toggle_with_valid_id(self):
        response = self.client.post('/todo/', data={
            'updateTodo': '1', 'todo_id': str(self.item.pk), 'completed': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertTrue(self.item.completed)

    def test_toggle_with_non_numeric_id_does_not_error(self):
        response = self.client.post('/todo/', data={
            'updateTodo': '1', 'todo_id': 'not-a-number', 'completed': 'on',
        })
        self.assertEqual(response.status_code, 302)

    def test_toggle_with_missing_id_does_not_error(self):
        response = self.client.post('/todo/', data={'updateTodo': '1', 'completed': 'on'})
        self.assertEqual(response.status_code, 302)
