"""AWWWZad2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from framacapp.views import home_view, file_view, add_dir_view, add_file_view, remove_file_dir_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('file/<str:filename>', file_view),
    path('add_file/', add_file_view),
    path('add_directory/', add_dir_view),
    path('remove_file_dir/', remove_file_dir_view),
    path('', home_view)
]
