from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    path('', views.todoPage, name='todo'),
    path('edit/<int:pk>/', views.todoEdit, name='todoEdit'),
    path('delete/<int:pk>/', views.todoDelete, name='todoDelete'),
]