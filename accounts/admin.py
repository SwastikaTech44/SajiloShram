from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('SajiloShram', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('SajiloShram', {'fields': ('role', 'phone')}),
    )
    list_display = ('username', 'role', 'phone', 'is_staff')
    list_filter = ('role',)