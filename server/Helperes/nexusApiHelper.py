"""
Nexus API Helper - Handles all interactions with the external Nexus API
for user data storage (replacing JSON file storage)
"""

import requests
from typing import Optional, List, Dict, Any
from modeles.user import User
from modeles.role import ROLE
from modeles.department import Department
import logging

logger = logging.getLogger(__name__)

class NexusApiHelper:
    """Helper class to interact with Nexus API for user data management"""
    
    BASE_URL = "http://192.168.0.253:5001"

    @staticmethod
    def saveCode(code,id):
        response = requests.post(
                f"{NexusApiHelper.BASE_URL}/invite/codes",
                timeout=10,
                json={
                    'code':code,
                    'id':id,
                    'max_uses' : 5, #badelha twali ml .env
                    'expires_in_days' : 60 #kima li fougha
                }
            )
        
    
    @staticmethod
    def _convert_role_to_nexus(role: ROLE) -> str:
        """Convert internal ROLE enum to Nexus API role format"""
        role_mapping = {
            ROLE.HR: "hr",
            ROLE.MANAGER: "manager",
            ROLE.EMPLOYER: "employee",
            ROLE.GUEST: "employee"
        }
        role_str = role.name if isinstance(role, ROLE) else role
        return role_mapping.get(ROLE[role_str] if isinstance(role_str, str) else role, "employee")
    
    @staticmethod
    def _convert_nexus_role_to_internal(nexus_role: str) -> ROLE:
        """Convert Nexus API role to internal ROLE enum"""
        role_mapping = {
            "hr": ROLE.HR,
            "manager": ROLE.MANAGER,
            "employee": ROLE.EMPLOYER
        }
        return role_mapping.get(nexus_role.lower(), ROLE.GUEST)
    
    @staticmethod
    def _convert_Department_to_nexus(Department) -> Optional[str]:
        """Convert internal Department enum to string"""
        if Department is None:
            return None
        return Department.name if isinstance(Department, Department) else str(Department)
    
    @staticmethod
    def _convert_nexus_Department_to_internal(dept_str: Optional[str]) -> Optional[Department]:
        """Convert Nexus Department string to internal Department enum"""
        if dept_str is None or dept_str == "":
            return None
        try:
            return Department[dept_str.upper()]
        except (KeyError, AttributeError):
            return None
    
    @staticmethod
    def create_user_in_nexus(user: User) -> bool:
        """
        Create a user in Nexus API
        Note: This is for DATA storage only, authentication is still handled by Supabase
        """
        
        try:
            user_data = {
                "email": user.Email,
                "password": "temp_password_not_used222",  # Nexus requires password field but we don't use it for auth
                "role": NexusApiHelper._convert_role_to_nexus(user.Role),
                "first_name": user.FirstName,
                "last_name": user.LastName,
                "address": user.Address,
                "Department": NexusApiHelper._convert_Department_to_nexus(user.Department),
                "userID": user.ID,  # Store our internal ID
                "date_of_birth": user.DateOfBirth,
                "code":11
            }
            
            response = requests.post(
                f"{NexusApiHelper.BASE_URL}/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info(f"✅ User created in Nexus API: {user.Email}")
                return True
            elif response.status_code == 409:
                logger.warning(f"⚠️ User already exists in Nexus API: {user.Email}")
                return True  # User exists is OK
            else:
                logger.error(f"❌ Failed to create user in Nexus API: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error creating user in Nexus API: {e}")
            return False
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Retrieve user from Nexus API by email
        Returns User object or None if not found
        """
        try:
            # First, get all users (Nexus API doesn't have get-by-email endpoint)
            # In production, you'd want to modify Nexus API to add this endpoint
            response = requests.get(
                f"{NexusApiHelper.BASE_URL}/users/",
                timeout=10
            )
            print("useres from massoud : ",response.json())
            if response.status_code != 200:
                logger.error(f"❌ Failed to get users from Nexus API: {response.status_code}")
                return None
            
            data = response.json()
            users = data.get("data", [])
            
            # Find user by email
            for user_data in users:
                if user_data.get("email", "").lower() == email.lower():
                    return NexusApiHelper._convert_nexus_user_to_internal(user_data)
            
            logger.info(f"User not found in Nexus API: {email}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting user from Nexus API: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(nexus_user_id: int) -> Optional[User]:
        """
        Retrieve user from Nexus API by Nexus user ID
        """
        try:
            response = requests.get(
                f"{NexusApiHelper.BASE_URL}/users/{nexus_user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("data", {})
                return NexusApiHelper._convert_nexus_user_to_internal(user_data)
            else:
                logger.error(f"❌ Failed to get user {nexus_user_id} from Nexus API: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting user from Nexus API: {e}")
            return None
    
    @staticmethod
    def get_all_users(role_filter: Optional[ROLE] = None) -> List[User]:
        """
        Get all users from Nexus API
        Optionally filter by role
        """
        try:
            response = requests.get(
                f"{NexusApiHelper.BASE_URL}/users/",
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get all users from Nexus API: {response.status_code}")
                return []
            
            data = response.json()
            users_data = data.get("data", [])
            
            users = [NexusApiHelper._convert_nexus_user_to_internal(user_data) for user_data in users_data]
            
            # Filter by role if specified
            if role_filter:
                users = [user for user in users if user.Role == role_filter]
            
            return users
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting all users from Nexus API: {e}")
            return []
    
    @staticmethod
    def update_user(user: User) -> bool:
        """
        Update user data in Nexus API
        """
        try:
            # First, find the user's Nexus ID by email
            nexus_user = NexusApiHelper.get_user_by_email(user.Email)
            if not nexus_user:
                logger.error(f"❌ Cannot update user - not found in Nexus API: {user.Email}")
                return False
            
            # Get Nexus ID from the returned user (stored in a custom field or ID)
            # For now, we'll search for it
            response = requests.get(f"{NexusApiHelper.BASE_URL}/users/", timeout=10)
            if response.status_code != 200:
                return False
            
            data = response.json()
            nexus_id = None
            for user_data in data.get("data", []):
                if user_data.get("email", "").lower() == user.Email.lower():
                    nexus_id = user_data.get("id")
                    break
            
            if not nexus_id:
                return False
            
            update_data = {
                "first_name": user.FirstName,
                "last_name": user.LastName,
                "address": user.Address,
                "Department": NexusApiHelper._convert_Department_to_nexus(user.Department),
                "role": NexusApiHelper._convert_role_to_nexus(user.Role)
            }
            
            response = requests.put(
                f"{NexusApiHelper.BASE_URL}/users/{nexus_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ User updated in Nexus API: {user.Email}")
                return True
            else:
                logger.error(f"❌ Failed to update user in Nexus API: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error updating user in Nexus API: {e}")
            return False
    
    @staticmethod
    def delete_user(email: str) -> bool:
        """
        Delete user from Nexus API
        """
        try:
            # Find the user's Nexus ID
            response = requests.get(f"{NexusApiHelper.BASE_URL}/users/", timeout=10)
            if response.status_code != 200:
                return False
            
            data = response.json()
            nexus_id = None
            for user_data in data.get("data", []):
                if user_data.get("email", "").lower() == email.lower():
                    nexus_id = user_data.get("id")
                    break
            
            if not nexus_id:
                logger.error(f"❌ User not found in Nexus API for deletion: {email}")
                return False
            
            response = requests.delete(
                f"{NexusApiHelper.BASE_URL}/users/{nexus_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ User deleted from Nexus API: {email}")
                return True
            else:
                logger.error(f"❌ Failed to delete user from Nexus API: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error deleting user from Nexus API: {e}")
            return False
    
    @staticmethod
    def _convert_nexus_user_to_internal(nexus_user_data: Dict[str, Any]) -> User:
        """
        Convert Nexus API user data to internal User object
        """
        user = User(
            Email=nexus_user_data.get("email", ""),
            FirstName=nexus_user_data.get("first_name", ""),
            LastName=nexus_user_data.get("last_name", ""),
            DateOfBirth=nexus_user_data.get("date_of_birth", ""),
            Address=nexus_user_data.get("address", "")
        )
        
        # Set ID (use userID if available, otherwise use nexus id as string)
        user.ID = nexus_user_data.get("userID", str(nexus_user_data.get("id", "")))
        
        # Set role
        user.Role = NexusApiHelper._convert_nexus_role_to_internal(nexus_user_data.get("role", "employee"))
        
        # Set Department
        user.Department = NexusApiHelper._convert_nexus_Department_to_internal(nexus_user_data.get("Department"))
        
        # Set employees list (if manager)
        user.EmployeesList = nexus_user_data.get("employeesList", [])
        
        return user
