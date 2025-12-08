"""
Health Check Helper - Handles service health checking operations
"""

import os
import requests


class HealthHelper:
    """Helper class for health check operations"""
    
    AUTH_SERVER = os.getenv('AUTH_SERVER')
    USER_SERVER = os.getenv('UserServices')
    DATA_SERVER = os.getenv('DATA_SERVER')
    MEET_SERVER = os.getenv('Meet_server')
    ACTIVITY_SERVER = os.getenv('Activity_server')
    
    @staticmethod
    def check_auth_service():
        """Check auth service health"""
        try:
            response = requests.get(
                f"http://{HealthHelper.AUTH_SERVER}/health",
                timeout=5
            )
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Auth service unreachable: {str(e)}"}, 503
        except Exception as e:
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def check_user_service():
        """Check user service health"""
        try:
            response = requests.get(
                f"http://{HealthHelper.USER_SERVER}/health",
                timeout=5
            )
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"User service unreachable: {str(e)}"}, 503
        except Exception as e:
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def check_data_service():
        """Check data service health"""
        try:
            response = requests.get(
                f"http://{HealthHelper.DATA_SERVER}/health",
                timeout=5
            )
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Data service unreachable: {str(e)}"}, 503
        except Exception as e:
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def check_meeting_service():
        """Check meeting service health"""
        try:
            response = requests.get(
                f"http://{HealthHelper.MEET_SERVER}/health",
                timeout=5
            )
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Meeting service unreachable: {str(e)}"}, 503
        except Exception as e:
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def check_activity_service():
        """Check activity service health"""
        try:
            response = requests.get(
                f"http://{HealthHelper.ACTIVITY_SERVER}/health",
                timeout=5
            )
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Activity service unreachable: {str(e)}"}, 503
        except Exception as e:
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def check_all_services():
        """Check all services health and return combined status"""
        services = {
            "auth": HealthHelper.check_auth_service(),
            "user": HealthHelper.check_user_service(),
            "data": HealthHelper.check_data_service(),
            "meeting": HealthHelper.check_meeting_service(),
            "activity": HealthHelper.check_activity_service()
        }
        
        all_healthy = all(status == 200 for _, status in services.values())
        
        return {
            "success": all_healthy,
            "services": {
                name: {"data": data, "status": status}
                for name, (data, status) in services.items()
            }
        }, 200 if all_healthy else 503
