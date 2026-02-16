from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from core.responses import APIResponse
from .models import Child, Assessment, AssessmentCategory, AssessmentPhoto
from .serializers import (
    ChildListSerializer, ChildDetailSerializer, ChildCreateSerializer,
    AssessmentSerializer, AssessmentListSerializer, AssessmentCategorySerializer,
    AssessmentPhotoSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    responses={200: ChildListSerializer(many=True)},
    parameters=[
        OpenApiParameter('search', OpenApiTypes.STR, description='Search by name or code'),
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number'),
    ],
    description="Get list of children for logged-in user's school"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def children_list(request):
    """Get list of children from user's school"""
    
    # Check if user has school assigned
    if not request.user.school:
        return APIResponse.error(
            errors={'school': 'User is not assigned to any school'},
            message="School assignment required",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    # Get children from user's school only
    queryset = Child.objects.filter(school=request.user.school)
    
    # Search functionality
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(
            Q(code__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Pagination (simple)
    page = int(request.query_params.get('page', 1))
    page_size = 20
    start = (page - 1) * page_size
    end = start + page_size
    
    children = queryset[start:end]
    total_count = queryset.count()
    
    serializer = ChildListSerializer(children, many=True)
    
    return APIResponse.success(
        data={
            'children': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        },
        message="Children retrieved successfully"
    )


@extend_schema(
    request=ChildCreateSerializer,
    responses={201: ChildDetailSerializer},
    description="Add new child to user's school"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def add_child(request):
    """Add new child"""
    
    # Check if user has school assigned
    if not request.user.school:
        return APIResponse.error(
            errors={'school': 'User is not assigned to any school'},
            message="School assignment required",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ChildCreateSerializer(data=request.data, context={'request': request})
    
    if not serializer.is_valid():
        return APIResponse.validation_error(
            errors=serializer.errors,
            message="Validation failed"
        )
    
    child = serializer.save()
    
    # Create pending assessments for all categories
    categories = AssessmentCategory.objects.filter(is_active=True)
    for category in categories:
        Assessment.objects.create(
            child=child,
            category=category,
            created_by=request.user
        )
    
    detail_serializer = ChildDetailSerializer(child)
    
    return APIResponse.created(
        data=detail_serializer.data,
        message="Child added successfully"
    )


@extend_schema(
    responses={200: ChildDetailSerializer},
    parameters=[
        OpenApiParameter('code', OpenApiTypes.STR, OpenApiParameter.PATH, description='Child code or QR code'),
    ],
    description="Get child details by code"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def child_detail(request, code):
    """Get child details by code"""
    
    child = get_object_or_404(Child, code=code)
    
    # Check if child belongs to user's school
    if child.school != request.user.school:
        return APIResponse.forbidden(
            message="You don't have permission to view this child"
        )
    
    serializer = ChildDetailSerializer(child)
    
    return APIResponse.success(
        data=serializer.data,
        message="Child details retrieved"
    )


@extend_schema(
    responses={200: AssessmentListSerializer(many=True)},
    parameters=[
        OpenApiParameter('code', OpenApiTypes.STR, OpenApiParameter.PATH, description='Child code'),
    ],
    description="Get list of assessments for a child"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def child_assessments(request, code):
    """Get assessments for a child"""
    
    child = get_object_or_404(Child, code=code)
    
    # Check permission
    if child.school != request.user.school:
        return APIResponse.forbidden(
            message="You don't have permission to view this child's assessments"
        )
    
    assessments = child.assessments.all()
    serializer = AssessmentListSerializer(assessments, many=True)
    
    return APIResponse.success(
        data={
            'child': ChildDetailSerializer(child).data,
            'assessments': serializer.data
        },
        message="Assessments retrieved"
    )


@extend_schema(
    request=AssessmentSerializer,
    responses={200: AssessmentSerializer},
    parameters=[
        OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description='Assessment ID'),
    ],
    description="Start or update assessment"
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_assessment(request, id):
    """Update assessment results"""
    
    assessment = get_object_or_404(Assessment, id=id)
    
    # Check permission
    if assessment.child.school != request.user.school:
        return APIResponse.forbidden(
            message="You don't have permission to update this assessment"
        )
    
    serializer = AssessmentSerializer(
        assessment, 
        data=request.data, 
        partial=True
    )
    
    if not serializer.is_valid():
        return APIResponse.validation_error(
            errors=serializer.errors,
            message="Validation failed"
        )
    
    # Update timestamps based on status
    if 'status' in request.data:
        if request.data['status'] == 'in_progress' and not assessment.started_at:
            from django.utils import timezone
            serializer.validated_data['started_at'] = timezone.now()
        elif request.data['status'] == 'completed':
            from django.utils import timezone
            serializer.validated_data['completed_at'] = timezone.now()
    
    serializer.save()
    
    return APIResponse.success(
        data=serializer.data,
        message="Assessment updated successfully"
    )


@extend_schema(
    responses={200: AssessmentCategorySerializer(many=True)},
    description="Get all assessment categories"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assessment_categories(request):
    """Get all assessment categories"""
    
    categories = AssessmentCategory.objects.filter(is_active=True)
    serializer = AssessmentCategorySerializer(categories, many=True)
    
    return APIResponse.success(
        data=serializer.data,
        message="Categories retrieved"
    )

@extend_schema(
    request={'multipart/form-data': {'type': 'object', 'properties': {'photo': {'type': 'string', 'format': 'binary'}}}},
    responses={200: ChildDetailSerializer},
    description="Upload photo for child"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_child_photo(request, code):
    """Upload photo for child"""
    
    child = get_object_or_404(Child, code=code)
    
    # Check permission
    if child.school != request.user.school:
        return APIResponse.forbidden(
            message="You don't have permission to update this child"
        )
    
    if 'photo' not in request.FILES:
        return APIResponse.validation_error(
            errors={'photo': 'Photo file is required'},
            message="Photo required"
        )
    
    child.photo = request.FILES['photo']
    child.save()
    
    serializer = ChildDetailSerializer(child)
    
    return APIResponse.success(
        data=serializer.data,
        message="Photo uploaded successfully"
    )
