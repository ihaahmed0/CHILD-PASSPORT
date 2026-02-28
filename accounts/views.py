from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from core.responses import APIResponse
from .serializers import LoginSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError


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


@extend_schema(
    request=TokenRefreshSerializer,
    responses={200: dict},
    description="Refresh access token using refresh token"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh Access Token
    
    Use the refresh token to get a new access token
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return APIResponse.validation_error(
            errors={'refresh': 'Refresh token is required'},
            message="Validation failed"
        )
    
    serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
    
    try:
        serializer.is_valid(raise_exception=True)
        
        return APIResponse.success(
            data={
                'access': serializer.validated_data['access'],
                'refresh': serializer.validated_data.get('refresh')  # In case rotation is enabled
            },
            message="Token refreshed successfully"
        )
    except TokenError as e:
        return APIResponse.error(
            errors={'refresh': 'Invalid or expired refresh token'},
            message="Token refresh failed",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return APIResponse.error(
            errors={'detail': str(e)},
            message="Token refresh failed",
            status_code=status.HTTP_400_BAD_REQUEST
        )