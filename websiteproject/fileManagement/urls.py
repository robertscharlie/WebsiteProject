from django.urls import path
from . import views

urlpatterns = [
    path('', views.fileViewPage, name='fileViewPage'),
    path('upload/', views.fileUploadPage, name='fileUploadPage'),
    path('download/<int:fileID>/', views.downloadFile, name='downloadFile'),
    path('edit/<int:fileID>/', views.fileEditPage, name='fileEditPage'),
    path('delete/<int:fileID>/', views.fileDeletePage, name='fileDeletePage'),
]
