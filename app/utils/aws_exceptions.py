from fastapi import HTTPException
from httpx import HTTPError
import json
from typing import Dict, Any

class AWSAuthError(Exception):
    """Base exception for AWS authentication errors"""
    pass

class AWSSignatureError(AWSAuthError):
    """Exception for AWS signature validation failures"""
    pass

class AWSCredentialsError(AWSAuthError):
    """Exception for AWS credential issues"""
    pass

def handle_dtech_error(error: Exception) -> HTTPException:
    """
    Convert DTech API errors to appropriate HTTP exceptions
    """
    if isinstance(error, AWSAuthError):
        return HTTPException(
            status_code=401,
            detail="Authentication failed with DTech API"
        )
    elif isinstance(error, HTTPError):
        # Try to parse the error response if available
        response = getattr(error, "response", None)
        if response is not None:
            try:
                error_content = response.json()
                return HTTPException(
                    status_code=response.status_code,
                    detail=error_content.get('error', str(error))
                )
            except (json.JSONDecodeError, ValueError):
                return HTTPException(
                    status_code=response.status_code,
                    detail=str(error)
                )
        else:
            return HTTPException(
                status_code=500,
                detail=str(error)
            )
    
    return HTTPException(status_code=500, detail=str(error))

async def validate_aws_response(response: Any) -> Dict:
    """
    Validate AWS API response and handle common errors
    """
    try:
        if response.status_code == 403:
            raise AWSSignatureError("Invalid AWS signature")
        elif response.status_code == 401:
            raise AWSCredentialsError("Invalid AWS credentials")
            
        response.raise_for_status()
        return response.json()
    except HTTPError as e:
        raise handle_dtech_error(e)
    except Exception as e:
        raise handle_dtech_error(e)
