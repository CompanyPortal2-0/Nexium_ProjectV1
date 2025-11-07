import uuid
from typing import Optional

from modeles.user import User
from testStore.userJson import JsonUserStore
from Helperes.passwordHelper import passwordHelper
from supaBase.supaBase import SupabaseConnectionSingleton


class userHelper:
    """User helper class with Supabase authentication integration"""
    
    def __init__(self, supabase_connection: SupabaseConnectionSingleton, use_supabase: bool = False):
        """
        Initialize userHelper with Supabase connection
        
        Args:
            supabase_connection: SupabaseConnectionSingleton instance for authentication
            use_supabase: Whether to actually use Supabase or just local storage
        """
        self.supabase = supabase_connection
        self.json_store = JsonUserStore("./userJson.json")
        self.use_supabase = use_supabase  # Flag to control Supabase usage
    
    def getUserByEmail(self, email: str) -> Optional[User]:
        """
        Get user by email from JSON storage
        
        Args:
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        all_users = self.json_store.get_all_users()
        for user in all_users:
            if user.Email == email:
                return user
        return None
    
    def getUserBySupabaseId(self, supabase_id: str) -> Optional[User]:
        """
        Get user by Supabase user ID
        
        Args:
            supabase_id: Supabase authentication user ID
            
        Returns:
            User object if found, None otherwise
        """
        all_users = self.json_store.get_all_users()
        for user in all_users:
            if user.ID == supabase_id:
                return user
        return None

    def CreateUser(self, Email: str, FirstName: str, LastName: str, 
                   DateOfBirth: str, Address: str, password: str) -> Optional[User]:
        """
        Create a new user with Supabase authentication
        
        Args:
            Email: User's email address
            FirstName: User's first name
            LastName: User's last name
            DateOfBirth: User's date of birth
            Address: User's address
            password: User's password (will be hashed by Supabase)
            
        Returns:
            User object if created successfully, None if email exists or creation failed
        """
        # Check if email already exists in local storage
        existing_user = self.getUserByEmail(Email)
        if existing_user is not None:
            return None
        
        # Create user in Supabase authentication (only if enabled)
        supabase_user_id = None
        if self.use_supabase:
            print(f"🔵 [SUPABASE] Attempting to create user: {Email}")
            try:
                supabase_user_id = self.supabase.sign_up_user(Email, password)
                if supabase_user_id is None:
                    # Supabase signup failed (email might already exist in Supabase)
                    print(f"⚠️ [SUPABASE] Signup failed for {Email} - returned None")
                    return None
                else:
                    print(f"✅ [SUPABASE] User created successfully with ID: {supabase_user_id}")
            except Exception as e:
                print(f"❌ [SUPABASE ERROR] Signup failed: {type(e).__name__}: {e}")
                print(f"   Falling back to local UUID generation")
                # Fallback: generate local UUID if Supabase fails
                supabase_user_id = str(uuid.uuid4())
        else:
            # Local-only mode: generate UUID directly without trying Supabase
            print(f"🔵 [LOCAL] Creating user with local UUID: {Email}")
            supabase_user_id = str(uuid.uuid4())
        
        # Create user in local JSON storage with Supabase ID
        newUser = User(
            Email=Email, 
            FirstName=FirstName, 
            LastName=LastName, 
            ID=supabase_user_id,  # Use Supabase ID as user ID
            DateOfBirth=DateOfBirth, 
            Address=Address, 
            EmployeesList=[]
        )
        self.json_store.add_user(newUser)
        
        # Store password locally as backup (using bcrypt)
        passwordHelper.assignPasswordToUser(newUser.ID, password)
        
        return newUser
    
    def authenticateUser(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user using Supabase
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Try Supabase authentication first (only if enabled)
        if self.use_supabase:
            print(f"🔵 [SUPABASE] Attempting to authenticate user: {email}")
            try:
                supabase_user_id = self.supabase.sign_in_user(email, password)
                if supabase_user_id is not None:
                    print(f"✅ [SUPABASE] Authentication successful, ID: {supabase_user_id}")
                    # Get user from local storage
                    user = self.getUserBySupabaseId(supabase_user_id)
                    if user is None:
                        print(f"⚠️ [SUPABASE] User {supabase_user_id} not found in local storage by ID")
                        # Fallback: try to find by email
                        user = self.getUserByEmail(email)
                        if user:
                            print(f"✅ [LOCAL] Found user by email instead: {user.ID}")
                        else:
                            print(f"❌ [LOCAL] User {email} not found in local storage at all")
                    return user
                else:
                    print(f"❌ [SUPABASE] Authentication failed - returned None")
            except Exception as e:
                print(f"❌ [SUPABASE ERROR] Authentication failed: {type(e).__name__}: {e}")
                print(f"   Falling back to local authentication")
        else:
            print(f"🔵 [LOCAL] Using local authentication for: {email}")
        
        # Local authentication (or fallback if Supabase fails)
        user = self.getUserByEmail(email)
        if user is not None:
            print(f"🔵 [LOCAL] Found user in JSON, checking password...")
            if passwordHelper.isPasswordTrueForUser(user.ID, password):
                print(f"✅ [LOCAL] Password verified successfully")
                return user
            else:
                print(f"❌ [LOCAL] Password verification failed")
        else:
            print(f"❌ [LOCAL] User {email} not found in local storage")
        
        return None

    def getAllUsers(self, type=None):
        """
        Get all users, optionally filtered by role
        
        Args:
            type: Role type to filter by (optional)
            
        Returns:
            List of User objects
        """
        users = self.json_store.get_all_users()
        if type is not None:
            users = [user for user in users if user.Role == type]
        return users

    def addEmployee(self, usr: User, emp: str):
        """
        Add an employee to a manager's employee list
        
        Args:
            usr: Manager user object
            emp: Employee email to add
        """
        if emp not in usr.EmployeesList:
            usr.EmployeesList.append(emp)
    
    def removeEmployee(self, user: User, emp: str):
        """
        Remove an employee from a manager's employee list
        
        Args:
            user: Manager user object
            emp: Employee email to remove
        """
        if emp in user.EmployeesList:
            user.EmployeesList.remove(emp)
