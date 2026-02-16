from django.contrib import admin
from .models import Location, School


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'school_count']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    
    def school_count(self, obj):
        return obj.schools.count()
    school_count.short_description = 'Number of Schools'


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'is_active', 'user_count', 'created_at']
    list_filter = ['location', 'is_active', 'created_at']
    search_fields = ['name', 'address', 'email']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'is_active')
        }),
        ('Contact Details', {
            'fields': ('address', 'phone', 'email')
        }),
    )
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Number of Users'