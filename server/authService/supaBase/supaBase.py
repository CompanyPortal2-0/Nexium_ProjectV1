import os
from supabase import create_client, Client, ClientOptions
import httpx
import logging

logger = logging.getLogger(__name__)


def create_supabase_client(url: str, key: str) -> Client:
    """Create a Supabase client with proper timeout and retry configuration"""
    timeout = httpx.Timeout(120.0, connect=30.0)
    http_client = httpx.Client(
        timeout=timeout,
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        follow_redirects=True
    )
    options = ClientOptions({
        'auth': {'http_client': http_client}
    })
    return create_client(url, key, options)


class dataBaseAuth:
    """
    Supabase Auth wrapper that uses:
    - ANON_KEY for user operations (signup, login) 
    - SERVICE_ROLE_KEY for admin operations (getUserById, deleteUser)
    """
    
    def __init__(self, url: str, anon_key: str, service_role_key: str):
        self.url = url
        self.anon_key = anon_key
        self.service_role_key = service_role_key
        
        # Client for user operations (signup, login)
        self.user_client: Client = create_supabase_client(url, anon_key)
        
        # We'll create admin client fresh for each request to avoid session pollution
        logger.info("Supabase Auth initialized with separate keys for user and admin operations")

    def _get_admin_client(self) -> Client:
        """
        Create a fresh admin client for each admin request.
        This prevents session pollution from user operations.
        """
        return create_supabase_client(self.url, self.service_role_key)

    def createUser(self, email: str, password: str):
        """Create a new user in Supabase Auth (uses ANON_KEY)"""
        try:
            response = self.user_client.auth.sign_up({
                "email": email,
                "password": password,
            })
            return response.model_dump_json()
        except httpx.RemoteProtocolError as e:
            logger.error(f"Supabase connection error during sign_up: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    def login(self, email: str, password: str):
        """Sign in user with email and password (uses ANON_KEY)"""
        try:
            response = self.user_client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            return response.model_dump_json()
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return None

    def delUser(self, userId: str):
        """Delete user by ID (admin operation - uses SERVICE_ROLE_KEY)"""
        try:
            admin_client = self._get_admin_client()
            response = admin_client.auth.admin.delete_user(userId)
            return response.model_dump_json()
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return None

    def getUserById(self, userId: str):
        """Get user information by user ID from Supabase Auth (admin operation - uses SERVICE_ROLE_KEY)"""
        try:
            admin_client = self._get_admin_client()
            response = admin_client.auth.admin.get_user_by_id(userId)
            return response.model_dump_json()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

