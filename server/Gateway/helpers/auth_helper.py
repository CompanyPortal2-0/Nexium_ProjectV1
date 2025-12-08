"""
Auth Helper
===========
Handles authentication-related business logic and communication with Auth Service.

Responsibilities:
    - User login
    - User signup
    - JWT identity resolution (user_id → email)
"""

import requests
import os
import logging
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class AuthHelper:
    """
    Helper class for authentication operations.
    Communicates with the Auth Service for user authentication and identity resolution.
    """
    
    AUTH_SERVER = os.getenv('AUTH_SERVER')
    TIMEOUT = 10
    
    @staticmethod
    def get_user_email_from_jwt_identity(user_id: str) -> Optional[str]:
        """
        Get user email from auth service using the JWT identity (user ID).
        This function is used whenever we need to resolve the user email from the JWT token.
        
        Args:
            user_id: The user ID extracted from JWT token using get_jwt_identity()
        
        Returns:
            str: User email if found, None otherwise
        """
        try:
            response = requests.get(
                f'http://{AuthHelper.AUTH_SERVER}/user/{user_id}/email',
                timeout=AuthHelper.TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("email")
            else:
                logger.warning(f"Failed to get user email: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting user email from auth service: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user email: {e}")
            return None
    
    @staticmethod
    def login(email: str, password: str) -> Tuple[Dict[str, Any], int]:
        """
        Forward login request to Auth Service.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            if not email or not password:
                return {"Text": "missing content"}, 401
            
            response = requests.post(
                f'http://{AuthHelper.AUTH_SERVER}/login',
                json={"email": email, "password": password},
                timeout=AuthHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Login service error: {e}")
            return {"error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {"error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def signup(
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        date_of_birth: str,
        address: str,
        manager_code: str = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Forward signup request to Auth Service.
        
        Args:
            email: User's email
            password: User's password
            first_name: User's first name
            last_name: User's last name
            date_of_birth: User's date of birth
            address: User's address
            manager_code: Optional manager invitation code
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Validate required fields
            if not all([email, first_name, last_name, password, date_of_birth, address]):
                return {"Text": "Missing required fields"}, 400
            
            response = requests.post(
                f'http://{AuthHelper.AUTH_SERVER}/signup',
                json={
                    "email": email,
                    "Password": password,
                    "FirstName": first_name,
                    "LastName": last_name,
                    "DateOfBirth": date_of_birth,
                    "Address": address,
                    "managercode": manager_code
                },
                timeout=AuthHelper.TIMEOUT
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                return {
                    "AuthToken": auth_data.get("Token"),
                    "id": auth_data.get("id"),
                    "firstname": first_name,
                    "lastname": last_name,
                    "role": "employee"
                }, 200
            else:
                return {"error": "we get an error from auth service"}, 500
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Signup service error: {e}")
            return {"error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Signup error: {e}")
            return {"error": f"Internal error: {str(e)}"}, 500
