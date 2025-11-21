import uuid
from supaBase.supaBase import dataBaseAuth
from modeles.user import User
from testStore.userJson import JsonUserStore
from Helperes.passwordHelper import passwordHelper
from Helperes.nexusApiHelper import NexusApiHelper
from modeles.role import ROLE
import logging

logger = logging.getLogger(__name__)


class userHelper:
    """
    User Helper - Now uses Nexus API for data storage instead of JSON files
    Authentication still handled by Supabase
    """

    @staticmethod
    def getUserByEmail(email: str) -> User:
        """Get user by email from Nexus API"""
        try:
            user = NexusApiHelper.get_user_by_email(email)
            if user:
                logger.info(f"✅ User retrieved from Nexus API: {email}")
            else:
                logger.info(f"⚠️ User not found in Nexus API: {email}")
            return user
        except Exception as e:
            logger.error(f"❌ Error getting user by email from Nexus API: {e}")
            return None

    @staticmethod
    def CreateUser(Email, FirstName, LastName, DateOfBirth, Address, password):
        """
        Create user in both Supabase (auth) and Nexus API (data storage)
        """
        try:
            # Generate unique ID
            ID = str(uuid.uuid4())
            
            # Create User object
            newUser = User(Email, FirstName, LastName, ID, DateOfBirth, Address, EmployeesList=[])
            
            # Store user in Nexus API
            success = NexusApiHelper.create_user_in_nexus(newUser)
            if not success:
                logger.error(f"❌ Failed to create user in Nexus API: {Email}")
                return False, None
            
            # Store password locally (still using passwordHelper)
            # passwordHelper.assignPasswordToUser(newUser.ID, password)
            
            logger.info(f"✅ User created successfully: {Email}")
            return True, newUser
            
        except Exception as e:
            logger.error(f"❌ Create user error: {e}")
            import traceback
            traceback.print_exc()
            return False, None

    @staticmethod
    def getAllUsers(type=None):
        """Get all users from Nexus API, optionally filtered by role"""
        try:
            users = NexusApiHelper.get_all_users(role_filter=type)
            logger.info(f"✅ Retrieved {len(users)} users from Nexus API")
            return users
        except Exception as e:
            logger.error(f"❌ Error getting all users from Nexus API: {e}")
            return []

    @staticmethod
    def removeEmployee(user, emp):
        """Remove employee from user's employees list"""
        try:
            if emp in user.EmployeesList:
                user.EmployeesList.remove(emp)
                # Update in Nexus API
                NexusApiHelper.update_user(user)
                logger.info(f"✅ Employee removed: {emp}")
        except Exception as e:
            logger.error(f"❌ Error removing employee: {e}")

    @staticmethod
    def assignCodeToManager(manager: User, code):
        """Assign manager code (still using JSON for codes)"""
        try:
            codes = JsonUserStore("./codes.json")
            codes.codeToMangaer(manager, code)
            logger.info(f"✅ Code assigned to manager: {manager.Email}")
        except Exception as e:
            logger.error(f"❌ Error assigning code to manager: {e}")
    
    @staticmethod
    def getManagerFromCode(code):
        """Get manager email from code (still using JSON for codes)"""
        try:
            data = JsonUserStore("./codes.json").get_all_code()
            for item in data:
                for user_id, stored_code in item.items():
                    if stored_code == code:
                        return user_id
            return None
        except Exception as e:
            logger.error(f"❌ Error getting manager from code: {e}")
            return None
    
    @staticmethod
    def addemployerTomanager(manager: User, user: User):
        """Add employee to manager's employees list and update in Nexus API"""
        try:
            # Add employee email to manager's list if not already present
            if user.Email not in manager.EmployeesList:
                manager.EmployeesList.append(user.Email)
            
            # Update manager in Nexus API
            success = NexusApiHelper.update_user(manager)
            
            if success:
                logger.info(f"✅ Employee {user.Email} added to manager {manager.Email}")
                return True
            else:
                logger.error(f"❌ Failed to update manager in Nexus API: {manager.Email}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error adding employer to manager: {e}")
            import traceback
            traceback.print_exc()
            return False

