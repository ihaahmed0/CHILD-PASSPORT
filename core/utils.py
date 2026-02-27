
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed, 
    NotAuthenticated, 
    PermissionDenied, 
    NotFound, 
    ValidationError
)
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied as DjangoPermissionDenied


def custom_exception_handler(exc, context):
    """
    Custom exception handler to ensure ALL errors follow unified format
    
    Unified Response Format:
    {
        "success": false,
        "status_code": 400,
        "message": "Error message",
        "data": null,
        "errors": {...}
    }
    """
    
    # Handle Django's Http404
    if isinstance(exc, Http404):
        exc = NotFound(detail='The requested resource was not found')
    
    # Handle Django's ObjectDoesNotExist
    if isinstance(exc, ObjectDoesNotExist):
        exc = NotFound(detail='The requested resource was not found')
    
    # Handle Django's PermissionDenied
    if isinstance(exc, DjangoPermissionDenied):
        exc = PermissionDenied(detail='You do not have permission to perform this action')
    
    # Handle JWT token errors
    if isinstance(exc, (InvalidToken, TokenError)):
        exc = AuthenticationFailed(detail='Token is invalid or expired')
    
    # Call REST framework's default exception handler
    response = exception_handler(exc, context)
    
    # If response is None, we have an unhandled exception (500 error)
    if response is None:
        return None
    
    # Create unified response structure
    custom_response = {
        'success': False,
        'status_code': response.status_code,
        'message': 'An error occurred',
        'data': None,
        'errors': {}
    }
    
    # Extract error details and meaningful message
    if isinstance(response.data, dict):
        custom_response['errors'] = response.data
        
        # Extract meaningful message
        if 'detail' in response.data:
            custom_response['message'] = str(response.data['detail'])
        elif 'non_field_errors' in response.data:
            if isinstance(response.data['non_field_errors'], list):
                custom_response['message'] = str(response.data['non_field_errors'][0])
            else:
                custom_response['message'] = str(response.data['non_field_errors'])
        else:
            # Get first error message from any field
            for key, value in response.data.items():
                if isinstance(value, list) and len(value) > 0:
                    custom_response['message'] = f"{key}: {value[0]}"
                    break
                elif isinstance(value, str):
                    custom_response['message'] = f"{key}: {value}"
                    break
    
    elif isinstance(response.data, list):
        custom_response['errors'] = {'detail': response.data}
        if response.data:
            custom_response['message'] = str(response.data[0])
    
    else:
        custom_response['errors'] = {'detail': str(response.data)}
        custom_response['message'] = str(response.data)
    
    # Set specific messages based on status code if no better message found
    if custom_response['message'] == 'An error occurred':
        if response.status_code == 400:
            custom_response['message'] = 'Bad request'
        elif response.status_code == 401:
            custom_response['message'] = 'Authentication required'
        elif response.status_code == 403:
            custom_response['message'] = 'Permission denied'
        elif response.status_code == 404:
            custom_response['message'] = 'Resource not found'
        elif response.status_code == 405:
            custom_response['message'] = 'Method not allowed'
        elif response.status_code == 500:
            custom_response['message'] = 'Internal server error'
    
    response.data = custom_response
    return response