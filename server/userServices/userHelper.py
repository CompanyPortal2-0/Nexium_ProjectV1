import requests
import logging
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Import models
from modeles.user import User
from modeles.role import ROLE
from modeles.department import Department

load_dotenv()

logger = logging.getLogger(__name__)


class userHelper:
    # Base URL for saving server
    SAVING_SERVER_URL = os.getenv('SAVING_server', 'http://127.0.0.1:5001')
    
    @staticmethod
    def getUserByEmail(email: str) -> Optional[User]:
        """Get user by email from Saving Server"""
        try:
            user = userHelper.get_user_by_email_from_SavingServer(email)
            if user:
                logger.info(f"✅ User retrieved from Saving Server: {email}")
            else:
                logger.info(f"⚠️ User not found in Saving Server: {email}")
            return user
        except Exception as e:
            logger.error(f"❌ Error getting user by email from Saving Server: {e}")
            return None

    @staticmethod
    def get_user_by_email_from_SavingServer(email: str) -> Optional[User]:
        """
        Retrieve user from Saving Server by email
        Returns User object or None if not found
        """
        try:
            # Get all users from Saving Server
            response = requests.get(
                f"{userHelper.SAVING_SERVER_URL}/users/",
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get users from Saving Server: {response.status_code}")
                return None
            
            data = response.json()
            users = data.get("data", [])
            
            # Find user by email
            for user_data in users:
                if user_data.get("email", "").lower() == email.lower():
                    return userHelper._convert_server_user_to_internal(user_data)
            
            logger.info(f"User not found in Saving Server: {email}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting user from Saving Server: {e}")
            return None
    
    @staticmethod
    def _convert_role_from_server(server_role: str) -> ROLE:
        """Convert server role string to internal ROLE enum"""
        role_mapping = {
            "hr": ROLE.HR,
            "manager": ROLE.MANAGER,
            "employee": ROLE.EMPLOYER
        }
        return role_mapping.get(server_role.lower(), ROLE.GUEST)
    
    @staticmethod
    def _convert_department_from_server(dept_str: Optional[str]) -> Optional[Department]:
        """Convert server department string to internal DEPARTMENT enum"""
        if dept_str is None or dept_str == "":
            return None
        try:
            return Department[dept_str.upper()]
        except (KeyError, AttributeError):
            return None
    
    @staticmethod
    def _convert_server_user_to_internal(user_data: Dict[str, Any]) -> User:
        """
        Convert Saving Server user data to internal User object
        """
        user = User(
            Email=user_data.get("email", ""),
            FirstName=user_data.get("first_name", ""),
            LastName=user_data.get("last_name", ""),
            DateOfBirth=user_data.get("date_of_birth", ""),
            Address=user_data.get("address", "")
        )
        
        # Set ID (use userID if available, otherwise use server id as string)
        user.ID = user_data.get("userID", str(user_data.get("id", "")))
        
        # Set role
        user.Role = userHelper._convert_role_from_server(user_data.get("role", "employee"))
        
        # Set department
        user.Department = userHelper._convert_department_from_server(user_data.get("department"))
        
        # Set employees list (if manager)
        user.EmployeesList = user_data.get("employeesList", [])
        
        return user
    