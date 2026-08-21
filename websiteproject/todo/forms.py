from django import forms
from .models import TodoItem

class TodoItemForm(forms.ModelForm):
    dueDate = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=True)
    remindDate = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=True)

    class Meta:
        model = TodoItem
        fields = ['title', 'priority', 'dueDate', 'remindDate']