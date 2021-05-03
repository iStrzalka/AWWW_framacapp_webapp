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
from django.urls import path, include
from framacapp.views import home_view, get_result, run_prover, load_file, \
    add_file, add_filep, add_dir, add_dirp, remove, removep, reload_tree

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add_file/', add_file),
    path('add_filep/', add_filep),
    path('add_dir/', add_dir),
    path('add_dirp/', add_dirp),
    path('remove/', remove),
    path('removep/', removep),
    path('run_prover/', run_prover),
    path('get_result/', get_result),
    path('load_file/', load_file),
    path('reload_tree/', reload_tree),
    path('', include("django.contrib.auth.urls")),
    path('', home_view)
]
