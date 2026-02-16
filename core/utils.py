from rest_framework.views import exception_handler
from rest_framework import status
from .responses import APIResponse


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework
    Returns responses in our unified format
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'status_code': response.status_code,
            'message': 'An error occurred',
            'data': None,
            'errors': {}
        }
        
        # Handle different types of errors
        if isinstance(response.data, dict):
            custom_response_data['errors'] = response.data
            
            # Try to extract a meaningful message
            if 'detail' in response.data:
                custom_response_data['message'] = str(response.data['detail'])
            elif 'error' in response.data:
                custom_response_data['message'] = str(response.data['error'])
            else:
                # Get first error message
                for key, value in response.data.items():
                    if isinstance(value, list) and len(value) > 0:
                        custom_response_data['message'] = f"{key}: {value[0]}"
                        break
        else:
            custom_response_data['errors'] = {'detail': str(response.data)}
            custom_response_data['message'] = str(response.data)
        
        response.data = custom_response_data
    
    return response