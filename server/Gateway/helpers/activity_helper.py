"""
Activity Helper
===============
Handles activity-related business logic and communication with Activity Service.

Responsibilities:
    - Activity CRUD operations (create, read, update, delete)
    - Activity participation (join, leave)
    - Participant management
    - User's activities retrieval
"""

import requests
import os
import logging
from typing import Dict, Any, Tuple, List, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ActivityHelper:
    """
    Helper class for activity operations.
    Communicates with the Activity Service for activity management.
    """
    
    ACTIVITY_SERVER = os.getenv('Activity_server', 'localhost:7056')
    TIMEOUT = 10
    
    # =================== CREATE OPERATIONS ===================
    
    @staticmethod
    def create_activity(data: Dict[str, Any], creator_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Create a new activity.
        
        Args:
            data: Activity data from request
            creator_email: Email of the user creating the activity
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            data['creator'] = creator_email
            
            response = requests.post(
                f'http://{ActivityHelper.ACTIVITY_SERVER}/activities',
                json=data,
                timeout=ActivityHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Create activity service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Create activity error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    # =================== READ OPERATIONS ===================
    
    @staticmethod
    def list_activities(params: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], int]:
        """
        List all activities with optional filters.
        
        Args:
            params: Query parameters for filtering
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.get(
                f'http://{ActivityHelper.ACTIVITY_SERVER}/activities',
                params=params,
                timeout=ActivityHelper.TIMEOUT
            )
            logger.info(f"Activity GET response: {response.json()}")
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"List activities service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"List activities error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def get_activity(activity_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Get a specific activity by ID.
        
        Args:
            activity_id: The activity ID
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.get(
                f'http://{ActivityHelper.ACTIVITY_SERVER}/activities/{activity_id}',
                timeout=ActivityHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get activity service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get activity error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def get_my_activities(user_email: str, filter_type: str = 'all') -> Tuple[Dict[str, Any], int]:
        """
        Get all activities for a specific user.
        
        Args:
            user_email: The user's email
            filter_type: Filter type ('all', 'created', 'joined')
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.post(
                f'http://{ActivityHelper.ACTIVITY_SERVER}/activities/my-activities',
                json={
                    'user_email': user_email,
                    'filter': filter_type
                },
                timeout=ActivityHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get my activities service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get my activities error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    # =================== UPDATE OPERATIONS ===================
    
    @staticmethod
    def update_activity(
        activity_id: int,
        data: Dict[str, Any],
        requester_email: str
    ) -> Tuple[Dict[str, Any], int]:
        """
        Update an activity.
        
        Args:
            activity_id: The activity ID
            data: Update data
            requester_email: Email of the user making the request
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            data['requester_email'] = requester_email
            
            response = requests.put(
                f'http://{ActivityHelper.ACTIVITY_SERVER}/activities/{activity_id}',
                json=data,
                timeout=ActivityHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Update activity service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Update activity error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    # =================== DELETE OPERATIONS ===================
    
    @staticmethod
    def delete_activity(activity_id: int, requester_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Delete an activity.
        
        Args:
            activity_id: The activity ID
            requester_email: Email of the user making the request
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.delete(
                f'http://{ActivityHelper.ACTIVITY_SERVER}/activities/{activity_id}',
                json={'requester_email': requester_email},
                timeout=ActivityHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Delete activity service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Delete activity error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    # =================== PARTICIPANT OPERATIONS ===================
    
    @staticmethod
    def join_activity(activity_id: int, employee_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Join an activity.
        
        Args:
            activity_id: The activity ID
            employee_email: Email of the employee joining
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.post(
                f'http://{ActivityHelper.ACTIVITY_SERVER}/activities/{activity_id}/join',
                json={'employee_email': employee_email},
                timeout=ActivityHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Join activity service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Join activity error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def leave_activity(activity_id: int, employee_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Leave an activity.
        
        Args:
            activity_id: The activity ID
            employee_email: Email of the employee leaving
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.post(
                f'http://{ActivityHelper.ACTIVITY_SERVER}/activities/{activity_id}/leave',
                json={'employee_email': employee_email},
                timeout=ActivityHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Leave activity service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Leave activity error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def add_participants(activity_id: int, emails: List[str]) -> Tuple[Dict[str, Any], int]:
        """
        Add multiple participants to an activity.
        
        Args:
            activity_id: The activity ID
            emails: List of participant emails to add
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.post(
                f'http://{ActivityHelper.ACTIVITY_SERVER}/activities/{activity_id}/add-participants',
                json={'emails': emails},
                timeout=ActivityHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Add participants service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Add participants error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def get_participants(activity_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Get all participants of an activity.
        
        Args:
            activity_id: The activity ID
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.get(
                f'http://{ActivityHelper.ACTIVITY_SERVER}/activities/{activity_id}/participants',
                timeout=ActivityHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get participants service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get participants error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def remove_participant(activity_id: int, participant_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Remove a participant from an activity.
        
        Args:
            activity_id: The activity ID
            participant_email: Email of the participant to remove
            
        Returns:
            Tuple of (response_data, status_code)
        """
        # Uses the leave endpoint to remove a participant
        return ActivityHelper.leave_activity(activity_id, participant_email)
    
    # =================== ALIAS METHODS FOR BACKWARD COMPATIBILITY ===================
    
    @staticmethod
    def create(data: Dict[str, Any], creator_email: str) -> Tuple[Dict[str, Any], int]:
        """Alias for create_activity"""
        return ActivityHelper.create_activity(data, creator_email)
    
    @staticmethod
    def list_all(params: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], int]:
        """Alias for list_activities"""
        return ActivityHelper.list_activities(params)
    
    @staticmethod
    def get_by_id(activity_id: int) -> Tuple[Dict[str, Any], int]:
        """Alias for get_activity"""
        return ActivityHelper.get_activity(activity_id)
    
    @staticmethod
    def update(activity_id: int, data: Dict[str, Any], requester_email: str) -> Tuple[Dict[str, Any], int]:
        """Alias for update_activity"""
        return ActivityHelper.update_activity(activity_id, data, requester_email)
    
    @staticmethod
    def delete(activity_id: int, requester_email: str) -> Tuple[Dict[str, Any], int]:
        """Alias for delete_activity"""
        return ActivityHelper.delete_activity(activity_id, requester_email)
    
    @staticmethod
    def join(activity_id: int, employee_email: str) -> Tuple[Dict[str, Any], int]:
        """Alias for join_activity"""
        return ActivityHelper.join_activity(activity_id, employee_email)
    
    @staticmethod
    def leave(activity_id: int, employee_email: str) -> Tuple[Dict[str, Any], int]:
        """Alias for leave_activity"""
        return ActivityHelper.leave_activity(activity_id, employee_email)
