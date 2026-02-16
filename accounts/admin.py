from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields to display in the user list
    list_display = ['username', 'email', 'first_name', 'last_name', 'school', 'is_active', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'school']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    # Fields to show when editing a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('School Assignment', {'fields': ('school',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields to show when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone'),
        }),
        ('School Assignment', {
            'fields': ('school',),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff'),
        }),
    )