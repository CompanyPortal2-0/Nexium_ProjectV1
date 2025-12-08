"""
User Helper
===========
Handles user-related business logic and communication with User Service.

Responsibilities:
    - Get teammates for a user
    - Get full team information
    - Manager code operations (generate, validate)
    - Become manager functionality
"""

import requests
import os
import logging
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class UserHelper:
    """
    Helper class for user operations.
    Communicates with the User Service for user data and team management.
    """
    
    USER_SERVICE = os.getenv('UserServices_server')
    TIMEOUT = 10
    
    @staticmethod
    def get_teammates(
        user_email: str,
        include_details: str = 'true',
        include_manager: str = 'true'
    ) -> Tuple[Dict[str, Any], int]:
        """
        Get all teammates of an employee (other employees under the same manager).
        
        Args:
            user_email: The email of the user to get teammates for
            include_details: If 'true', returns full user objects instead of just emails
            include_manager: If 'true', includes manager information in response
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.get(
                f'http://{UserHelper.USER_SERVICE}/users/{user_email}/teammates',
                params={
                    'include_details': include_details,
                    'include_manager': include_manager
                },
                timeout=UserHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get teammates service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get teammates error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def get_full_team(user_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Get full team information for a user.
        Returns full team info including the employee, their manager, and all teammates with details.
        
        Args:
            user_email: The email of the user to get team info for
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.get(
                f'http://{UserHelper.USER_SERVICE}/users/{user_email}/team',
                timeout=UserHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get team service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get team error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def get_code_for_manager(manager_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Generate an invitation code for a manager to invite employees.
        
        Args:
            manager_email: The email of the manager requesting the code
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            if not manager_email:
                return {"Text": "Manager email is required"}, 400
            
            response = requests.post(
                f'http://{UserHelper.USER_SERVICE}/getCodeForManager',
                json={"manager_email": manager_email},
                timeout=UserHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get manager code service error: {e}")
            return {"Text": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get manager code error: {e}")
            return {"Text": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def become_manager(user_email: str, code: str) -> Tuple[Dict[str, Any], int]:
        """
        Process request for a user to become a manager using a code.
        
        Args:
            user_email: The email of the user requesting to become manager
            code: The manager promotion code
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.post(
                f'http://{UserHelper.USER_SERVICE}/becameManger',
                json={"code": code, "userMail": user_email},
                timeout=UserHelper.TIMEOUT
            )
            logger.info(f"Become manager response: {response.json()}")
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Become manager service error: {e}")
            return {"error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Become manager error: {e}")
            return {"error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def generate_became_manager_code(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Generate a code that allows a user to become a manager.
        
        Args:
            data: Request data containing necessary information
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.get(
                f'http://{UserHelper.USER_SERVICE}/generateBecameManagerCode',
                json=data,
                timeout=UserHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Generate became manager code service error: {e}")
            return {"error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Generate became manager code error: {e}")
            return {"error": str(e)}, 500
