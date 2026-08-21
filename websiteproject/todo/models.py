from django.db import models

# Create your models here.

class TodoItem(models.Model):
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]
    # ordering weight for sort-by-priority (higher sorts first)
    PRIORITY_ORDER = {PRIORITY_HIGH: 0, PRIORITY_MEDIUM: 1, PRIORITY_LOW: 2}

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    dueDate = models.DateTimeField(null=True, blank=True)
    remindDate = models.DateTimeField(null=True, blank=True)
    reminderSent = models.BooleanField(default=False)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID:{self.pk}, TITLE:{self.title}, USER:{self.user.username}"

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if self.pk and (update_fields is None or 'remindDate' in update_fields):
            previous = TodoItem.objects.filter(pk=self.pk).values('remindDate').first()
            if previous and previous['remindDate'] != self.remindDate:
                self.reminderSent = False
        super().save(*args, **kwargs)