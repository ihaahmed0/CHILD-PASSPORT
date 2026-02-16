from rest_framework import serializers
from .models import Child, AssessmentCategory, Assessment, AssessmentPhoto


class ChildListSerializer(serializers.ModelSerializer):
    """Serializer for listing children"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    location_name = serializers.CharField(source='school.location.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    assessment_progress = serializers.IntegerField(source='get_assessment_progress', read_only=True)
    completed_assessments = serializers.IntegerField(source='get_completed_assessments_count', read_only=True)
    
    class Meta:
        model = Child
        fields = [
            'id', 'code', 'qr_code', 'first_name', 'last_name', 'full_name',
            'age', 'gender', 'dominant_hand', 'photo',
            'school', 'school_name', 'location_name',
            'assessment_progress', 'completed_assessments',
            'created_at'
        ]
        read_only_fields = ['id', 'code', 'qr_code', 'created_at']


class ChildDetailSerializer(serializers.ModelSerializer):
    """Serializer for child details"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    location_name = serializers.CharField(source='school.location.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    assessment_progress = serializers.IntegerField(source='get_assessment_progress', read_only=True)
    
    class Meta:
        model = Child
        fields = [
            'id', 'code', 'qr_code', 'first_name', 'last_name', 'full_name',
            'age', 'gender', 'dominant_hand', 'photo',
            'school', 'school_name', 'location_name',
            'assessment_progress', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'qr_code', 'created_at', 'updated_at']


class ChildCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating children"""
    
    class Meta:
        model = Child
        fields = [
            'first_name', 'last_name', 'age', 'gender', 
            'dominant_hand', 'photo'
        ]
    
    def create(self, validated_data):
        # Get user's school from request context
        user = self.context['request'].user
        validated_data['school'] = user.school
        validated_data['created_by'] = user
        return super().create(validated_data)


class AssessmentCategorySerializer(serializers.ModelSerializer):
    """Serializer for assessment categories"""
    
    class Meta:
        model = AssessmentCategory
        fields = ['id', 'name', 'description', 'order']


class AssessmentPhotoSerializer(serializers.ModelSerializer):
    """Serializer for assessment photos"""
    
    class Meta:
        model = AssessmentPhoto
        fields = ['id', 'photo_type', 'photo', 'notes', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for assessments"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    child_code = serializers.CharField(source='child.code', read_only=True)
    child_name = serializers.CharField(source='child.get_full_name', read_only=True)
    photos = AssessmentPhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Assessment
        fields = [
            'id', 'child', 'child_code', 'child_name',
            'category', 'category_name', 'status',
            'results', 'notes', 'photos',
            'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']


class AssessmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing child's assessments"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_order = serializers.IntegerField(source='category.order', read_only=True)
    photo_count = serializers.IntegerField(source='photos.count', read_only=True)
    
    class Meta:
        model = Assessment
        fields = [
            'id', 'category', 'category_name', 'category_order',
            'status', 'photo_count', 'completed_at'
        ]