from rest_framework import serializers
from .models import Location, School


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model"""
    school_count = serializers.IntegerField(source='schools.count', read_only=True)
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'description', 'school_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for School model"""
    location_name = serializers.CharField(source='location.name', read_only=True)
    user_count = serializers.IntegerField(source='users.count', read_only=True)
    
    class Meta:
        model = School
        fields = [
            'id',
            'name',
            'location',
            'location_name',
            'address',
            'phone',
            'email',
            'is_active',
            'user_count',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']