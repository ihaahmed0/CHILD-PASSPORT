from django.contrib import admin
from django.utils.html import format_html
from .models import Child, AssessmentCategory, Assessment, AssessmentPhoto


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'first_name', 'last_name', 'age', 'gender', 
        'school', 'assessment_progress', 'created_at'
    ]
    list_filter = ['gender', 'dominant_hand', 'school', 'created_at']
    search_fields = ['code', 'first_name', 'last_name']
    readonly_fields = ['code', 'qr_code', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'qr_code', 'first_name', 'last_name', 'age', 'gender', 'dominant_hand')
        }),
        ('Photo', {
            'fields': ('photo',)
        }),
        ('School Assignment', {
            'fields': ('school',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def assessment_progress(self, obj):
        progress = obj.get_assessment_progress()
        color = 'green' if progress == 100 else 'orange' if progress > 0 else 'gray'
        return format_html(
            '<span style="color: {};">{} %</span>',
            color, progress
        )
    assessment_progress.short_description = 'Progress'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AssessmentCategory)
class AssessmentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'assessment_count']
    list_editable = ['order', 'is_active']
    search_fields = ['name']
    
    def assessment_count(self, obj):
        return obj.assessments.count()
    assessment_count.short_description = 'Total Assessments'


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = [
        'child', 'category', 'status', 
        'started_at', 'completed_at'
    ]
    list_filter = ['status', 'category', 'completed_at']
    search_fields = ['child__code', 'child__first_name', 'child__last_name']
    readonly_fields = ['started_at', 'completed_at']
    
    fieldsets = (
        ('Assessment Info', {
            'fields': ('child', 'category', 'status')
        }),
        ('Results', {
            'fields': ('results', 'notes')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AssessmentPhoto)
class AssessmentPhotoAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'photo_type', 'uploaded_at']
    list_filter = ['photo_type', 'uploaded_at']
    search_fields = ['assessment__child__code']