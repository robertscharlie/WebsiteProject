from django.db import models

# Create your models here.

class TodoItem(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    dueDate = models.DateTimeField(null=True, blank=True)
    remindDate = models.DateTimeField(null=True, blank=True)
    reminderSent = models.BooleanField(default=False)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID:{self.pk}, TITLE:{self.title}, USER:{self.user.username}"

    def save(self, *args, **kwargs):
        if self.pk:
            previous = TodoItem.objects.filter(pk=self.pk).values('remindDate').first()
            if previous and previous['remindDate'] != self.remindDate:
                self.reminderSent = False
        super().save(*args, **kwargs)