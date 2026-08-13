from django.db import models

# Create your models here.

class TodoItem(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    dueDate = models.DateTimeField(null=True, blank=True)
    remindDate = models.DateTimeField(null=True, blank=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID:{self.pk}, TITLE:{self.title}, USER:{self.user.username}"