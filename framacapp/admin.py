from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OrigUserAdmin

from .models import Directory, File, User, Section


# Register your models here.
class UserAdmin(OrigUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = (
        'id', 'username', 'password', 'name'
    )
    readonly_fields = ['date_joined', 'last_login']
    filter_horizontal = []
    list_filter = []


admin.site.register(Directory)
admin.site.register(File)
admin.site.register(User, UserAdmin)
admin.site.register(Section)
