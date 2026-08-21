"""
URL configuration for websiteproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('files/', include('fileManagement.urls')),
    path('todo/', include('todo.urls')),
    path('server/', include('serverInfo.urls')),
    path('random/', include('randomTools.urls')),
]

# Uploaded files are private and must only be reachable through the
# authenticated, ownership-checked fileManagement.views.downloadFile view.
# Do NOT add django.conf.urls.static.static() for MEDIA_URL here: it would
# serve every file under MEDIA_ROOT (including other users' uploads) to
# anyone, with no login or ownership check, whenever DEBUG=True.