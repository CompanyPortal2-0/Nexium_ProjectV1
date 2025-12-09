"""
Gateway Helpers Package
=======================
This package contains helper classes for each microservice domain.
Each helper handles the business logic and communication with its respective microservice.

Structure:
    - auth_helper.py: Authentication operations (login, signup, JWT identity resolution)
    - user_helper.py: User service operations (teammates, team, manager codes)
    - activity_helper.py: Activity service operations (CRUD, join/leave, participants)
    - meeting_helper.py: Meeting service operations (create, join, CRUD, logs)
    - health_helper.py: Health check operations for downstream services
    - data_helper.py: File/data operations (upload, download, list files)
"""

from .auth_helper import AuthHelper
from .user_helper import UserHelper
from .activity_helper import ActivityHelper
from .meeting_helper import MeetingHelper
from .health_helper import HealthHelper
from .data_helper import DataHelper

__all__ = [
    'AuthHelper',
    'UserHelper', 
    'ActivityHelper',
    'MeetingHelper',
    'HealthHelper',
    'DataHelper'
]
