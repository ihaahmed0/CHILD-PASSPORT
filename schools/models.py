from django.db import models


class Location(models.Model):
    """
    Geographical location (city, region, etc.)
    Each location can have multiple schools
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
    
    def __str__(self):
        return self.name


class School(models.Model):
    """
    School associated with a location
    Each school can have multiple users
    """
    name = models.CharField(max_length=200)
    location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='schools'
    )
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'School'
        verbose_name_plural = 'Schools'
        unique_together = ['name', 'location']  # Same school name allowed in different locations
    
    def __str__(self):
        return f"{self.name} ({self.location.name})"