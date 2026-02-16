from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import random
import string


def generate_child_code():
    """Generate unique 7-digit code for child"""
    return ''.join(random.choices(string.digits, k=7))


def child_photo_path(instance, filename):
    """Generate upload path for child photos"""
    ext = filename.split('.')[-1]
    return f'children/photos/{instance.code}.{ext}'


class Child(models.Model):
    """Child/Case Model"""
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    HAND_CHOICES = [
        ('right', 'Right'),
        ('left', 'Left'),
    ]
    
    # Basic Information
    code = models.CharField(
        max_length=7, 
        unique=True, 
        editable=False,
        help_text="Auto-generated unique code"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(18)],
        help_text="Age in years"
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dominant_hand = models.CharField(max_length=10, choices=HAND_CHOICES)
    
    # Photo
    photo = models.ImageField(
        upload_to=child_photo_path,
        blank=True,
        null=True
    )
    
    # QR Code (same as code)
    qr_code = models.CharField(
        max_length=7,
        editable=False,
        help_text="QR code data (same as code)"
    )
    
    # School Assignment
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='children'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_children'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Child'
        verbose_name_plural = 'Children'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['school']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.code})"
    
    def save(self, *args, **kwargs):
        # Generate code if not exists
        if not self.code:
            self.code = generate_child_code()
            # Ensure uniqueness
            while Child.objects.filter(code=self.code).exists():
                self.code = generate_child_code()
        
        # Set QR code same as code
        if not self.qr_code:
            self.qr_code = self.code
        
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """Return child's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_assessment_progress(self):
        """Calculate assessment completion percentage"""
        total_assessments = 4  # Height & Weight, Posture, Flexibility, Range of Motion
        completed = self.assessments.filter(status='completed').count()
        return int((completed / total_assessments) * 100) if total_assessments > 0 else 0
    
    def get_completed_assessments_count(self):
        """Get count of completed assessments"""
        return self.assessments.filter(status='completed').count()


class AssessmentCategory(models.Model):
    """Assessment Category (Height & Weight, Posture, etc.)"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Assessment Category'
        verbose_name_plural = 'Assessment Categories'
    
    def __str__(self):
        return self.name


class Assessment(models.Model):
    """Assessment Result for a Child"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    category = models.ForeignKey(
        AssessmentCategory,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Results stored as JSON
    results = models.JSONField(
        default=dict,
        blank=True,
        help_text="Assessment results in JSON format"
    )
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Metadata
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assessments'
    )
    
    class Meta:
        ordering = ['-completed_at', '-started_at']
        verbose_name = 'Assessment'
        verbose_name_plural = 'Assessments'
        unique_together = ['child', 'category']
    
    def __str__(self):
        return f"{self.child.get_full_name()} - {self.category.name}"


def assessment_photo_path(instance, filename):
    """Generate upload path for assessment photos"""
    ext = filename.split('.')[-1]
    child_code = instance.assessment.child.code
    category = instance.assessment.category.name.lower().replace(' ', '_')
    return f'assessments/{child_code}/{category}/{instance.photo_type}.{ext}'


class AssessmentPhoto(models.Model):
    """Photos for assessments (mainly posture screening)"""
    
    PHOTO_TYPE_CHOICES = [
        ('face_view', 'Face View'),
        ('side_view', 'Side View'),
        ('back_view', 'Back View'),
    ]
    
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPE_CHOICES)
    photo = models.ImageField(upload_to=assessment_photo_path)
    notes = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['photo_type']
        verbose_name = 'Assessment Photo'
        verbose_name_plural = 'Assessment Photos'
        unique_together = ['assessment', 'photo_type']
    
    def __str__(self):
        return f"{self.assessment.child.code} - {self.photo_type}"