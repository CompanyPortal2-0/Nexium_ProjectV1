import requests
import logging
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from modeles.activity import Activity, ActivityType, ActivityStatus

load_dotenv()

logger = logging.getLogger(__name__)


class ActivityHelper:
    """
    Helper class for Activity operations.
    Communicates with the Saving Server for CRUD operations on activities.
    """
    
    SAVING_SERVER_URL = os.getenv('SAVING_server')
    HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}
    
    # =================== CREATE OPERATIONS ===================
    
    @staticmethod
    def create_activity(
        date: str,
        creator: str,
        activity_type: str,
        title: str = None,
        description: str = None,
        employees_joined: List[str] = None,
        status: str = "scheduled"
    ) -> Dict[str, Any]:
        """
        Create a new activity.
        
        Args:
            date: ISO format datetime (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD)
            creator: Email of the user creating the activity
            activity_type: Type of activity (meeting, training, etc.)
            title: Optional title for the activity
            description: Optional description
            employees_joined: Optional list of participant emails
            status: Activity status (default: scheduled)
            
        Returns:
            Dictionary with success status and activity data or error
        """
        try:
            # Validate activity type
            if not ActivityType.is_valid(activity_type):
                return {
                    "success": False,
                    "error": f"Invalid activity type: {activity_type}. Valid types: {ActivityType.get_all_types()}"
                }
            
            # Validate status if provided
            if status and not ActivityStatus.is_valid(status):
                return {
                    "success": False,
                    "error": f"Invalid status: {status}. Valid statuses: {ActivityStatus.get_all_statuses()}"
                }
            
            # Prepare payload
            payload = {
                "date": date,
                "creator": creator,
                "type": activity_type.lower(),
                "title": title,
                "description": description,
                "employees_joined": employees_joined or [],
                "status": status.lower() if status else "scheduled"
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            # Send request to Saving Server
            response = requests.post(
                f"{ActivityHelper.SAVING_SERVER_URL}/activities/",
                json=payload,
                headers=ActivityHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"✅ Activity created successfully: {data.get('data', {}).get('activity_id')}")
                return {
                    "success": True,
                    "message": "Activity created successfully",
                    "data": data.get("data", data)
                }
            else:
                error_data = response.json() if response.text else {"error": "Unknown error"}
                logger.error(f"❌ Failed to create activity: {response.status_code} - {error_data}")
                return {
                    "success": False,
                    "error": error_data.get("error", f"Failed to create activity: {response.status_code}")
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error creating activity: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Error creating activity: {e}")
            return {"success": False, "error": str(e)}
    
    # =================== READ OPERATIONS ===================
    
    @staticmethod
    def get_all_activities(
        creator: str = None,
        activity_type: str = None,
        status: str = None,
        employee: str = None,
        from_date: str = None,
        to_date: str = None
    ) -> Dict[str, Any]:
        """
        Get all activities with optional filtering.
        
        Args:
            creator: Filter by creator email
            activity_type: Filter by activity type
            status: Filter by status
            employee: Filter activities where this employee has joined
            from_date: Filter activities from this date
            to_date: Filter activities until this date
            
        Returns:
            Dictionary with success status and list of activities
        """
        try:
            # Build query parameters
            params = {}
            if creator:
                params["creator"] = creator
            if activity_type:
                params["type"] = activity_type
            if status:
                params["status"] = status
            if employee:
                params["employee"] = employee
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date
            
            response = requests.get(
                f"{ActivityHelper.SAVING_SERVER_URL}/activities/",
                params=params,
                headers=ActivityHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                activities = data.get("data", [])
                logger.info(f"✅ Retrieved {len(activities)} activities")
                return {
                    "success": True,
                    "count": len(activities),
                    "data": activities
                }
            else:
                logger.error(f"❌ Failed to get activities: {response.status_code}")
                return {"success": False, "error": f"Failed to get activities: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting activities: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Error getting activities: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_activity_by_id(activity_id: str) -> Dict[str, Any]:
        """
        Get a specific activity by its ID.
        
        Args:
            activity_id: The activity_id (UUID) or numeric id
            
        Returns:
            Dictionary with success status and activity data
        """
        try:
            response = requests.get(
                f"{ActivityHelper.SAVING_SERVER_URL}/activities/{activity_id}",
                headers=ActivityHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Retrieved activity: {activity_id}")
                return {
                    "success": True,
                    "data": data.get("data", data)
                }
            elif response.status_code == 404:
                logger.info(f"⚠️ Activity not found: {activity_id}")
                return {"success": False, "error": "Activity not found"}
            else:
                logger.error(f"❌ Failed to get activity: {response.status_code}")
                return {"success": False, "error": f"Failed to get activity: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting activity: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Error getting activity: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_user_activities(
        user_email: str,
        filter_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Get all activities for a specific user.
        
        Args:
            user_email: The user's email
            filter_type: 'all', 'created', or 'joined'
            
        Returns:
            Dictionary with success status and list of activities
        """
        try:
            params = {"filter": filter_type} if filter_type != "all" else {}
            
            response = requests.get(
                f"{ActivityHelper.SAVING_SERVER_URL}/activities/user/{user_email}",
                params=params,
                headers=ActivityHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                activities = data.get("data", [])
                logger.info(f"✅ Retrieved {len(activities)} activities for user {user_email}")
                return {
                    "success": True,
                    "user": user_email,
                    "filter": filter_type,
                    "count": len(activities),
                    "data": activities
                }
            elif response.status_code == 404:
                return {"success": False, "error": "User not found"}
            else:
                logger.error(f"❌ Failed to get user activities: {response.status_code}")
                return {"success": False, "error": f"Failed to get user activities: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting user activities: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Error getting user activities: {e}")
            return {"success": False, "error": str(e)}
    
    # =================== UPDATE OPERATIONS ===================
    
    @staticmethod
    def update_activity(
        activity_id: str,
        title: str = None,
        description: str = None,
        activity_type: str = None,
        date: str = None,
        employees_joined: List[str] = None,
        status: str = None
    ) -> Dict[str, Any]:
        """
        Update an existing activity.
        
        Args:
            activity_id: The activity to update
            title: New title (optional)
            description: New description (optional)
            activity_type: New type (optional)
            date: New date (optional)
            employees_joined: New list of participants (optional)
            status: New status (optional)
            
        Returns:
            Dictionary with success status and updated activity data
        """
        try:
            # Build update payload with only provided fields
            payload = {}
            
            if title is not None:
                payload["title"] = title
            if description is not None:
                payload["description"] = description
            if activity_type is not None:
                if not ActivityType.is_valid(activity_type):
                    return {
                        "success": False,
                        "error": f"Invalid activity type: {activity_type}"
                    }
                payload["type"] = activity_type.lower()
            if date is not None:
                payload["date"] = date
            if employees_joined is not None:
                payload["employees_joined"] = employees_joined
            if status is not None:
                if not ActivityStatus.is_valid(status):
                    return {
                        "success": False,
                        "error": f"Invalid status: {status}"
                    }
                payload["status"] = status.lower()
            
            if not payload:
                return {"success": False, "error": "No fields to update"}
            
            response = requests.put(
                f"{ActivityHelper.SAVING_SERVER_URL}/activities/{activity_id}",
                json=payload,
                headers=ActivityHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Activity updated: {activity_id}")
                return {
                    "success": True,
                    "message": "Activity updated successfully",
                    "data": data.get("data", data)
                }
            elif response.status_code == 404:
                return {"success": False, "error": "Activity not found"}
            else:
                error_data = response.json() if response.text else {}
                logger.error(f"❌ Failed to update activity: {response.status_code}")
                return {"success": False, "error": error_data.get("error", f"Failed to update: {response.status_code}")}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error updating activity: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Error updating activity: {e}")
            return {"success": False, "error": str(e)}
    
    # =================== DELETE OPERATIONS ===================
    
    @staticmethod
    def delete_activity(activity_id: str) -> Dict[str, Any]:
        """
        Delete an activity.
        
        Args:
            activity_id: The activity to delete
            
        Returns:
            Dictionary with success status
        """
        try:
            response = requests.delete(
                f"{ActivityHelper.SAVING_SERVER_URL}/activities/{activity_id}",
                headers=ActivityHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Activity deleted: {activity_id}")
                return {
                    "success": True,
                    "message": "Activity deleted successfully",
                    "deleted_activity": data.get("deleted_activity", {"activity_id": activity_id})
                }
            elif response.status_code == 404:
                return {"success": False, "error": "Activity not found"}
            else:
                logger.error(f"❌ Failed to delete activity: {response.status_code}")
                return {"success": False, "error": f"Failed to delete activity: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error deleting activity: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Error deleting activity: {e}")
            return {"success": False, "error": str(e)}
    
    # =================== PARTICIPANT OPERATIONS ===================
    
    @staticmethod
    def join_activity(activity_id: str, employee_email: str) -> Dict[str, Any]:
        """
        Add an employee to an activity's participants list.
        
        Args:
            activity_id: The activity to join
            employee_email: Email of the employee to add
            
        Returns:
            Dictionary with success status
        """
        try:
            payload = {"employee_email": employee_email}
            
            response = requests.post(
                f"{ActivityHelper.SAVING_SERVER_URL}/activities/{activity_id}/join",
                json=payload,
                headers=ActivityHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Employee {employee_email} joined activity {activity_id}")
                return {
                    "success": True,
                    "message": f"Employee {employee_email} joined the activity",
                    "data": data.get("data", data)
                }
            elif response.status_code == 404:
                error_data = response.json() if response.text else {}
                return {"success": False, "error": error_data.get("error", "Activity or employee not found")}
            elif response.status_code == 409:
                return {"success": False, "error": "Employee is already in this activity"}
            else:
                error_data = response.json() if response.text else {}
                logger.error(f"❌ Failed to join activity: {response.status_code}")
                return {"success": False, "error": error_data.get("error", f"Failed to join: {response.status_code}")}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error joining activity: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Error joining activity: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def leave_activity(activity_id: str, employee_email: str) -> Dict[str, Any]:
        """
        Remove an employee from an activity's participants list.
        
        Args:
            activity_id: The activity to leave
            employee_email: Email of the employee to remove
            
        Returns:
            Dictionary with success status
        """
        try:
            payload = {"employee_email": employee_email}
            
            response = requests.post(
                f"{ActivityHelper.SAVING_SERVER_URL}/activities/{activity_id}/leave",
                json=payload,
                headers=ActivityHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Employee {employee_email} left activity {activity_id}")
                return {
                    "success": True,
                    "message": f"Employee {employee_email} left the activity",
                    "data": data.get("data", data)
                }
            elif response.status_code == 404:
                error_data = response.json() if response.text else {}
                return {"success": False, "error": error_data.get("error", "Activity not found or employee not in activity")}
            else:
                logger.error(f"❌ Failed to leave activity: {response.status_code}")
                return {"success": False, "error": f"Failed to leave activity: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error leaving activity: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Error leaving activity: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_activity_participants(
        activity_id: str,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Get all participants of an activity.
        
        Args:
            activity_id: The activity ID
            include_details: If True, return full user objects
            
        Returns:
            Dictionary with success status and participants list
        """
        try:
            params = {"include_details": "true"} if include_details else {}
            
            response = requests.get(
                f"{ActivityHelper.SAVING_SERVER_URL}/activities/{activity_id}/participants",
                params=params,
                headers=ActivityHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Retrieved participants for activity {activity_id}")
                return {
                    "success": True,
                    "activity_id": activity_id,
                    "title": data.get("title"),
                    "creator": data.get("creator"),
                    "participants": data.get("participants", []),
                    "participants_count": data.get("participants_count", 0)
                }
            elif response.status_code == 404:
                return {"success": False, "error": "Activity not found"}
            else:
                logger.error(f"❌ Failed to get participants: {response.status_code}")
                return {"success": False, "error": f"Failed to get participants: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting participants: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Error getting participants: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def add_participants_by_emails(
        activity_id: str,
        emails: List[str]
    ) -> Dict[str, Any]:
        """
        Add multiple participants to an activity by their emails.
        
        Args:
            activity_id: The activity ID
            emails: List of participant emails to add
            
        Returns:
            Dictionary with success status and results for each email
        """
        results = {
            "success": True,
            "activity_id": activity_id,
            "added": [],
            "failed": [],
            "already_joined": []
        }
        
        for email in emails:
            result = ActivityHelper.join_activity(activity_id, email)
            if result.get("success"):
                results["added"].append(email)
            elif "already in this activity" in result.get("error", "").lower():
                results["already_joined"].append(email)
            else:
                results["failed"].append({
                    "email": email,
                    "error": result.get("error", "Unknown error")
                })
        
        # Set overall success based on results
        results["success"] = len(results["failed"]) == 0
        results["message"] = f"Added {len(results['added'])} participants, {len(results['already_joined'])} already joined, {len(results['failed'])} failed"
        
        return results
