"""
Meeting Helper
==============
Handles meeting-related business logic and communication with Meeting Service.

Responsibilities:
    - Meeting CRUD operations (create, read, update, delete)
    - Meeting lifecycle (start, end)
    - Meeting room access
    - Meeting logs
    - User's meetings retrieval
"""

import requests
import os
import logging
from typing import Dict, Any, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class MeetingHelper:
    """
    Helper class for meeting operations.
    Communicates with the Meeting Service for meeting management.
    """
    
    MEET_SERVER = os.getenv('Meet_server')
    MYIP = os.getenv('myip', 'localhost:7050')
    TIMEOUT = 10
    SSL_VERIFY = False  # For self-signed certificates
    
    # =================== CREATE OPERATIONS ===================
    
    @staticmethod
    def create_meeting(data: Dict[str, Any], creator_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Create a new meeting.
        
        Args:
            data: Meeting data from request
            creator_email: Email of the user creating the meeting
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            logger.info(f"Creating meeting for user: {creator_email}")
            data['created_by'] = creator_email
            
            response = requests.post(
                f"{MeetingHelper.MEET_SERVER}/create-meet",
                json=data,
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Create meeting service error: {e}")
            return {"error": "Gateway error"}, 500
        except Exception as e:
            logger.error(f"Create meeting error: {e}")
            return {"error": "Gateway error"}, 500
    
    @staticmethod
    def join_meeting(data: Dict[str, Any], user_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Join an existing meeting.
        
        Args:
            data: Join request data (meet_id, password, etc.)
            user_email: Email of the user joining
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            logger.info("Forwarding join-meet request to backend")
            data['user_email'] = user_email
            
            response = requests.post(
                f"{MeetingHelper.MEET_SERVER}/join-meet",
                json=data,
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                # Rewrite redirect URL to use gateway IP
                if 'redirectUrl' in result:
                    original_url = result['redirectUrl']
                    path = original_url.split('/', 3)[-1] if '/' in original_url else ''
                    result['redirectUrl'] = f"https://{MeetingHelper.MYIP}:7050/{path}"
                return result, response.status_code
            
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Join meeting service error: {e}")
            return {"error": "Gateway error"}, 500
        except Exception as e:
            logger.error(f"Join meeting error: {e}")
            return {"error": "Gateway error"}, 500
    
    @staticmethod
    def get_room_page(meet_id: str, user_email: str) -> Tuple[str, int]:
        """
        Get the meeting room HTML page.
        
        Args:
            meet_id: The meeting ID
            user_email: The user's email
            
        Returns:
            Tuple of (html_content, status_code)
        """
        try:
            logger.info(f"Forwarding room request for {meet_id}/{user_email}")
            
            response = requests.get(
                f"{MeetingHelper.MEET_SERVER}/room/{meet_id}/{user_email}",
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            
            if response.status_code == 200:
                html_content = response.text
                # Rewrite server URL in the HTML
                html_content = html_content.replace(
                    "SERVER='GatweyIP'",
                    f"SERVER='https://{MeetingHelper.MYIP}:7050'"
                )
                return html_content, 200
            else:
                return response.text, response.status_code
                
        except Exception as e:
            logger.error(f"Get room page error: {e}")
            return "Gateway error", 500
    
    # =================== READ OPERATIONS ===================
    
    @staticmethod
    def get_all_meetings(
        user_email: Optional[str] = None,
        is_active: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Get all meetings with optional filters.
        
        Args:
            user_email: Filter by user email
            is_active: Filter by active status
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            params = {}
            if user_email:
                params['user_email'] = user_email
            if is_active:
                params['is_active'] = is_active
            
            response = requests.get(
                f"{MeetingHelper.MEET_SERVER}/meetings",
                params=params,
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except Exception as e:
            logger.error(f"Get all meetings error: {e}")
            return {"error": "Gateway error"}, 500
    
    @staticmethod
    def get_meeting(meeting_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Get a specific meeting by ID.
        
        Args:
            meeting_id: The meeting ID
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.get(
                f"{MeetingHelper.MEET_SERVER}/meetings/{meeting_id}",
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except Exception as e:
            logger.error(f"Get meeting error: {e}")
            return {"error": "Gateway error"}, 500
    
    @staticmethod
    def get_my_meetings(
        user_email: str,
        filter_type: str = 'all',
        is_active: Optional[str] = None,
        include_details: str = 'false'
    ) -> Tuple[Dict[str, Any], int]:
        """
        Get all meetings for a specific user.
        
        Args:
            user_email: The user's email
            filter_type: Filter type ('all', 'created', 'invited')
            is_active: Filter by active status
            include_details: Include creator details
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            params = {'filter': filter_type, 'include_details': include_details}
            if is_active:
                params['is_active'] = is_active
            
            response = requests.get(
                f"{MeetingHelper.MEET_SERVER}/meetings/user/{user_email}",
                params=params,
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get my meetings service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get my meetings error: {e}")
            return {"success": False, "error": "Gateway error"}, 500
    
    @staticmethod
    def get_user_meetings(
        email: str,
        filter_type: str = 'all',
        is_active: Optional[str] = None,
        include_details: str = 'false'
    ) -> Tuple[Dict[str, Any], int]:
        """
        Get all meetings for a specific user by email.
        This method calls the /meetings/user/<email> endpoint.
        
        Args:
            email: The user's email
            filter_type: Filter type ('all', 'created', 'invited')
            is_active: Filter by active status
            include_details: Include creator details
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            params = {'filter': filter_type, 'include_details': include_details}
            if is_active:
                params['is_active'] = is_active
            
            response = requests.get(
                f"{MeetingHelper.MEET_SERVER}/meetings/user/{email}",
                params=params,
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get user meetings service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get user meetings error: {e}")
            return {"success": False, "error": "Gateway error"}, 500
    
    @staticmethod
    def get_my_upcoming_meetings(user_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Get all upcoming meetings for the currently logged-in user.
        This method calls the /meetings/user/<email>/upcoming endpoint.
        
        Args:
            user_email: The user's email
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.get(
                f"{MeetingHelper.MEET_SERVER}/meetings/user/{user_email}/upcoming",
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get my upcoming meetings service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get my upcoming meetings error: {e}")
            return {"success": False, "error": "Gateway error"}, 500
    
    @staticmethod
    def get_user_upcoming_meetings(email: str) -> Tuple[Dict[str, Any], int]:
        """
        Get all upcoming meetings for a specific user by email.
        This method calls the /meetings/user/<email>/upcoming endpoint.
        
        Args:
            email: The user's email
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.get(
                f"{MeetingHelper.MEET_SERVER}/meetings/user/{email}/upcoming",
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get user upcoming meetings service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get user upcoming meetings error: {e}")
            return {"success": False, "error": "Gateway error"}, 500
    
    @staticmethod
    def get_upcoming_meetings(user_email: str) -> Tuple[Dict[str, Any], int]:
        """
        DEPRECATED: Use get_my_upcoming_meetings or get_user_upcoming_meetings instead.
        Get all upcoming meetings for a specific user.
        
        Args:
            user_email: The user's email
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.get(
                f"{MeetingHelper.MEET_SERVER}/meetings/user/{user_email}/upcoming",
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get upcoming meetings service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get upcoming meetings error: {e}")
            return {"success": False, "error": "Gateway error"}, 500
    
    # =================== UPDATE OPERATIONS ===================
    
    @staticmethod
    def update_meeting(meeting_id: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Update a meeting.
        
        Args:
            meeting_id: The meeting ID
            data: Update data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.put(
                f"{MeetingHelper.MEET_SERVER}/meetings/{meeting_id}",
                json=data,
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except Exception as e:
            logger.error(f"Update meeting error: {e}")
            return {"error": "Gateway error"}, 500
    
    # =================== DELETE OPERATIONS ===================
    
    @staticmethod
    def delete_meeting(meeting_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Delete a meeting (basic delete).
        
        Args:
            meeting_id: The meeting ID
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.delete(
                f"{MeetingHelper.MEET_SERVER}/meetings/{meeting_id}",
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except Exception as e:
            logger.error(f"Delete meeting error: {e}")
            return {"error": "Gateway error"}, 500
    
    @staticmethod
    def soft_delete_meeting(meeting_id: str, user_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Soft delete a meeting (only creator can delete).
        
        Args:
            meeting_id: The meeting ID
            user_email: Email of the user requesting deletion
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.delete(
                f"{MeetingHelper.MEET_SERVER}/meetings/{meeting_id}/delete",
                json={"user_email": user_email},
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Soft delete meeting service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Soft delete meeting error: {e}")
            return {"success": False, "error": "Gateway error"}, 500
    
    @staticmethod
    def delete_meeting_by_user(meeting_id: str, user_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Soft delete a meeting by user (alias for soft_delete_meeting).
        Only the creator can delete. Calls /meetings/<meeting_id>/delete endpoint.
        
        Args:
            meeting_id: The meeting ID
            user_email: Email of the user requesting deletion
            
        Returns:
            Tuple of (response_data, status_code)
        """
        return MeetingHelper.soft_delete_meeting(meeting_id, user_email)
    
    @staticmethod
    def hard_delete_meeting(
        meeting_id: str,
        user_email: str,
        confirm: bool = False
    ) -> Tuple[Dict[str, Any], int]:
        """
        Permanently delete a meeting (only creator can delete, requires confirmation).
        
        Args:
            meeting_id: The meeting ID
            user_email: Email of the user requesting deletion
            confirm: Confirmation flag
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.delete(
                f"{MeetingHelper.MEET_SERVER}/meetings/{meeting_id}/hard-delete",
                json={"user_email": user_email, "confirm": confirm},
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Hard delete meeting service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Hard delete meeting error: {e}")
            return {"success": False, "error": "Gateway error"}, 500
    
    # =================== LIFECYCLE OPERATIONS ===================
    
    @staticmethod
    def start_meeting(meeting_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Start a meeting.
        
        Args:
            meeting_id: The meeting ID
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.post(
                f"{MeetingHelper.MEET_SERVER}/meetings/{meeting_id}/start",
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except Exception as e:
            logger.error(f"Start meeting error: {e}")
            return {"error": "Gateway error"}, 500
    
    @staticmethod
    def end_meeting(meeting_id: str) -> Tuple[Dict[str, Any], int]:
        """
        End a meeting.
        
        Args:
            meeting_id: The meeting ID
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.post(
                f"{MeetingHelper.MEET_SERVER}/meetings/{meeting_id}/end",
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except Exception as e:
            logger.error(f"End meeting error: {e}")
            return {"error": "Gateway error"}, 500
    
    # =================== LOG OPERATIONS ===================
    
    @staticmethod
    def add_log_entry(meeting_id: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Add a log entry to a meeting.
        
        Args:
            meeting_id: The meeting ID
            data: Log entry data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            response = requests.post(
                f"{MeetingHelper.MEET_SERVER}/meetings/{meeting_id}/log",
                json=data,
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except Exception as e:
            logger.error(f"Add log entry error: {e}")
            return {"error": "Gateway error"}, 500
    
    @staticmethod
    def get_meeting_log(
        meeting_id: str,
        download: Optional[str] = None
    ) -> Tuple[Any, int, Optional[Dict]]:
        """
        Get meeting logs.
        
        Args:
            meeting_id: The meeting ID
            download: If set, downloads as file
            
        Returns:
            Tuple of (content, status_code, headers) - headers only for downloads
        """
        try:
            params = {}
            if download:
                params['download'] = download
            
            response = requests.get(
                f"{MeetingHelper.MEET_SERVER}/meetings/{meeting_id}/log",
                params=params,
                verify=MeetingHelper.SSL_VERIFY,
                timeout=MeetingHelper.TIMEOUT
            )
            
            if download and response.status_code == 200:
                # Return file content with headers
                return response.content, response.status_code, dict(response.headers)
            else:
                return response.json(), response.status_code, None
                
        except Exception as e:
            logger.error(f"Get meeting log error: {e}")
            return {"error": "Gateway error"}, 500, None
