from supabase import create_client, Client
import threading
from dataclasses import dataclass


@dataclass
class SupabaseConfig:
    url: str
    key: str

class SupabaseConnectionSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config: SupabaseConfig):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.supabase = create_client(config.url, config.key)
        return cls._instance

    def sign_up_user(self, email: str, password: str):
        """Auth: Create user, return ID so you can save coordinates elsewhere."""
        result = self.supabase.auth.sign_up({"email": email, "password": password})
        if not result or not result.user:
            return None
        return result.user.id  # <---- Use this to store coordinates in your DB

    def sign_in_user(self, email: str, password: str):
        """Auth: Verify credentials, return user id."""
        result = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
        if not result or not result.user:
            return None
        return result.user.id  # <---- Use this to fetch coordinates later
