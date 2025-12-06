import secrets
import string
from flask import jsonify
import requests
import logging
import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Import models
from modeles.user import User
from modeles.role import ROLE
from modeles.department import Department

load_dotenv()

logger = logging.getLogger(__name__)


class userHelper:
    SAVING_SERVER_URL = os.getenv('SAVING_server')
    HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}
    
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
                headers=userHelper.HEADERS,
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
    

    @staticmethod
    def generateCode():
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    @staticmethod
    def saveIntoSavingServer(data,args):
        try:
            save_operations = {
                "managerCode": userHelper._save_manager_code,
                "becameManagerCode": userHelper._save_became_manager_code
                # Add more operations here as needed
                
            }
            
            # Get the appropriate save function
            save_function = save_operations.get(args)
            
            if save_function is None:
                logger.error(f"❌ Unknown operation type: {args}")
                return False, {"error": f"Unknown operation: {args}"}, 400
            
            # Execute the save operation
            return save_function(data)
            
        except Exception as e:
            logger.error(f"❌ Error in saveIntoSavingServer: {e}")
            return False, {"error": str(e)}, 500

    @staticmethod
    def _save_manager_code(data):
        
        try:
           
            # Prepare payload
            payload = {
                "manager_id": data.get("manager_id"),
                "code": data.get("code"),
                "max_uses": data.get("max_uses", 1)  # Default to 1 if not provided
            }
            
            # Send request to Saving Server
            response = requests.post(
                f"{userHelper.SAVING_SERVER_URL}/invites/manager",
                json=payload,
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            # Check response
            if response.status_code in [200, 201]:
                logger.info(f"✅ Manager code saved successfully: {data.get('code')}")
                return True, response.json() if response.text else {"success": True}, response.status_code
            else:
                logger.error(f"❌ Failed to save manager code: {response.status_code}")
                return False, {"error": "Failed to save code to database"}, response.status_code
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error saving manager code: {e}")
            return False, {"error": f"Database communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"❌ Error saving manager code: {e}")
            return False, {"error": str(e)}, 500

    @staticmethod
    def _save_became_manager_code(data):
        
        try:
            
            # Prepare payload
            payload = {
                "hrid": data.get("hrid"),
                "code": data.get("code"),
                "max_uses": data.get("max_uses", 1)  # Default to 1 if not provided
            }
            
            # Send request to Saving Server
            response = requests.post(
                f"{userHelper.SAVING_SERVER_URL}/manager_codes/becameManagerCode",
                json=payload,
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            # Check response
            if response.status_code in [200, 201]:
                logger.info(f"✅ Manager code saved successfully: {data.get('code')}")
                return True, response.json() if response.text else {"success": True}, response.status_code
            else:
                logger.error(f"❌ Failed to save manager code: {response.status_code}")
                return False, {"error": "Failed to save code to database"}, response.status_code
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error saving manager code: {e}")
            return False, {"error": f"Database communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"❌ Error saving manager code: {e}")
            return False, {"error": str(e)}, 500
    
    @staticmethod
    def make_employee_manager(code,userMail):
        if(userHelper.verify_became_manager_code(code)):
            employee = userHelper.get_user_by_email_from_SavingServer(userMail)
            employee.setRole(ROLE.MANAGER)
            
            userHelper.update_user(employee.getId(),employee.to_dict())
            return "done"
        else :
            return "invalid code"



    @staticmethod
    def update_user(user_id, user_data):
        try:
            response = requests.put(
                f"{userHelper.SAVING_SERVER_URL}/users/{user_id}",
                json=user_data,
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                return True
            return False
                
        except Exception as e:
            logger.error(f"❌ Error updating user: {e}")
            return False
    @staticmethod
    def verify_became_manager_code(code):
        try:
            response = requests.get(
                f"{userHelper.SAVING_SERVER_URL}/manager_codes/becameManagerCode/{code}",
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            return False
                
        except Exception as e:
            logger.error(f"❌ Error verifying became manager code: {e}")
            return False