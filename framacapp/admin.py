from django.contrib import admin

from .models import Directory, File, User, Section
# Register your models here.
admin.site.register(Directory)
admin.site.register(File)
admin.site.register(User)
admin.site.register(Section)
