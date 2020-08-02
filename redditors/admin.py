from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from redditors.models import User


# admin.site.register(User, UserAdmin)

class AccountAdmin(UserAdmin):
    list_display = (
    'pk', 'email', 'username', 'date_joined', 'last_login', 'is_verified_aadharcard', 'is_admin', 'is_staff', 'is_superuser', 'karma')
    search_fields = ('pk', 'email', 'username',)
    readonly_fields = ('pk', 'date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(User, AccountAdmin)
