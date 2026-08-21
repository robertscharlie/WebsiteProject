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


class TodoSearchFilterSortTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dana', password='pw')
        self.client.force_login(self.user)
        now = timezone.now()
        self.low = TodoItem.objects.create(
            user=self.user, title='Buy milk', priority=TodoItem.PRIORITY_LOW,
            dueDate=now + timedelta(days=3), remindDate=now + timedelta(days=2),
        )
        self.high = TodoItem.objects.create(
            user=self.user, title='File taxes', priority=TodoItem.PRIORITY_HIGH,
            dueDate=now + timedelta(days=1), remindDate=now + timedelta(hours=1),
        )
        self.done = TodoItem.objects.create(
            user=self.user, title='Buy eggs', completed=True, priority=TodoItem.PRIORITY_MEDIUM,
            dueDate=now + timedelta(days=1), remindDate=now + timedelta(hours=1),
        )

    def test_search_filters_by_title(self):
        response = self.client.get('/todo/', {'q': 'milk'})
        titles = [t.title for t in response.context['todos']]
        self.assertEqual(titles, ['Buy milk'])

    def test_status_filter_active(self):
        response = self.client.get('/todo/', {'status': 'active'})
        titles = {t.title for t in response.context['todos']}
        self.assertEqual(titles, {'Buy milk', 'File taxes'})

    def test_status_filter_completed(self):
        response = self.client.get('/todo/', {'status': 'completed'})
        titles = {t.title for t in response.context['todos']}
        self.assertEqual(titles, {'Buy eggs'})

    def test_sort_by_priority_orders_high_first_within_incomplete(self):
        response = self.client.get('/todo/', {'sort': 'priority'})
        titles = [t.title for t in response.context['todos']]
        # incomplete items first (completed sorts last), high priority before low
        self.assertEqual(titles.index('File taxes'), 0)
        self.assertLess(titles.index('File taxes'), titles.index('Buy milk'))
        self.assertEqual(titles[-1], 'Buy eggs')

    def test_invalid_sort_falls_back_to_default(self):
        response = self.client.get('/todo/', {'sort': 'nonsense'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['sort'], 'due')

    def test_create_preserves_current_filters(self):
        response = self.client.post(
            '/todo/?status=active&sort=priority',
            data={
                'title': 'New task', 'priority': 'high',
                'dueDate': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
                'remindDate': (timezone.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('status=active', response.url)
        self.assertIn('sort=priority', response.url)


class TodoOverdueTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='erin', password='pw')
        self.client.force_login(self.user)

    def test_overdue_item_is_flagged_in_context(self):
        past = timezone.now() - timedelta(days=1)
        TodoItem.objects.create(
            user=self.user, title='Late task', dueDate=past, remindDate=past,
        )
        response = self.client.get('/todo/')
        self.assertContains(response, 'Overdue')
        self.assertContains(response, 'class="todoBox overdue"')

    def test_completed_item_not_flagged_overdue(self):
        past = timezone.now() - timedelta(days=1)
        TodoItem.objects.create(
            user=self.user, title='Late but done', completed=True, dueDate=past, remindDate=past,
        )
        response = self.client.get('/todo/')
        self.assertNotContains(response, 'Overdue')
