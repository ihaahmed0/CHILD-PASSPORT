from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from core.responses import APIResponse
from .serializers import LoginSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter


@extend_schema(
    request=LoginSerializer,
    responses={200: UserSerializer},
    description="Login with username and password to get JWT tokens"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User Login API
    
    Returns JWT access and refresh tokens along with user info
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return APIResponse.validation_error(
            errors=serializer.errors,
            message="Invalid input"
        )
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user is None:
        return APIResponse.error(
            errors={'credentials': 'Invalid username or password'},
            message="Authentication failed",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return APIResponse.error(
            errors={'user': 'User account is disabled'},
            message="Account disabled",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    # Serialize user data
    user_serializer = UserSerializer(user)
    
    return APIResponse.success(
        data={
            'user': user_serializer.data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        },
        message="Login successful"
    )


@extend_schema(
    responses={200: UserSerializer},
    description="Get current logged-in user information"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Get Current User Info
    
    Returns information about the currently authenticated user
    """
    serializer = UserSerializer(request.user)
    return APIResponse.success(
        data=serializer.data,
        message="User info retrieved"
    )