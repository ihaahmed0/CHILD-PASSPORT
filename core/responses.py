from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """
    Unified API Response Structure
    
    Standard response format:
    {
        "success": true/false,
        "status_code": 200,
        "message": "Success message",
        "data": {...},
        "errors": null
    }
    """
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """
        Return successful response
        
        Args:
            data: Response data (dict, list, or None)
            message: Success message
            status_code: HTTP status code
        """
        return Response({
            'success': True,
            'status_code': status_code,
            'message': message,
            'data': data,
            'errors': None
        }, status=status_code)
    
    @staticmethod
    def error(errors, message="An error occurred", status_code=status.HTTP_400_BAD_REQUEST):
        """
        Return error response
        
        Args:
            errors: Error details (dict or list)
            message: Error message
            status_code: HTTP status code
        """
        return Response({
            'success': False,
            'status_code': status_code,
            'message': message,
            'data': None,
            'errors': errors
        }, status=status_code)
    
    @staticmethod
    def created(data=None, message="Created successfully"):
        """Return 201 Created response"""
        return APIResponse.success(
            data=data, 
            message=message, 
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def no_content(message="Deleted successfully"):
        """Return 204 No Content response"""
        return Response({
            'success': True,
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': message,
            'data': None,
            'errors': None
        }, status=status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def unauthorized(message="Authentication required"):
        """Return 401 Unauthorized response"""
        return APIResponse.error(
            errors={'detail': 'Invalid or missing authentication credentials'},
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(message="Permission denied"):
        """Return 403 Forbidden response"""
        return APIResponse.error(
            errors={'detail': 'You do not have permission to perform this action'},
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def not_found(message="Resource not found"):
        """Return 404 Not Found response"""
        return APIResponse.error(
            errors={'detail': 'The requested resource was not found'},
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def validation_error(errors, message="Validation failed"):
        """Return 400 Validation Error response"""
        return APIResponse.error(
            errors=errors,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )