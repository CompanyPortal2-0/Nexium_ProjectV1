"""
Activity Manager Service
========================
This service manages team activities and events.
It provides endpoints for creating, reading, updating, and deleting activities,
as well as managing participants.

Port: 7053
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

from activityHelper import ActivityHelper
from modeles.activity import ActivityType, ActivityStatus

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

SAVING_server = os.getenv('SAVING_server')


# =================== HEALTH CHECK ===================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "activity-manager",
        "version": "1.0.0"
    }), 200


# =================== CREATE OPERATIONS ===================

@app.route('/activities', methods=['POST'])
def create_activity():
    """
    Create a new activity.
    
    Expected JSON body:
    {
        "date": "2025-12-15T14:00:00",
        "creator": "manager@company.com",  // Set by Gateway from JWT
        "type": "training",
        "title": "Python Advanced Training",
        "description": "Advanced Python programming techniques",
        "employees_joined": ["employee1@company.com"],
        "status": "scheduled"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Request body is required"}), 400
        
        # Required fields
        date = data.get('date')
        creator = data.get('creator')
        activity_type = data.get('type')
        
        if not date:
            return jsonify({"success": False, "error": "Missing required field: date"}), 422
        if not creator:
            return jsonify({"success": False, "error": "Missing required field: creator"}), 422
        if not activity_type:
            return jsonify({"success": False, "error": "Missing required field: type"}), 422
        
        # Optional fields
        title = data.get('title')
        description = data.get('description')
        employees_joined = data.get('employees_joined', [])
        status = data.get('status', 'scheduled')
        
        # Create activity using helper
        result = ActivityHelper.create_activity(
            date=date,
            creator=creator,
            activity_type=activity_type,
            title=title,
            description=description,
            employees_joined=employees_joined,
            status=status
        )
        
        if result.get("success"):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in create_activity: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# =================== READ OPERATIONS ===================

@app.route('/activities', methods=['GET'])
def get_all_activities():
    """
    Get all activities with optional filtering.
    
    Query Parameters:
        - creator: Filter by creator email
        - type: Filter by activity type
        - status: Filter by status
        - employee: Filter activities where this employee has joined
        - from_date: Filter activities from this date
        - to_date: Filter activities until this date
    """
    try:
        # Get filter parameters
        creator = request.args.get('creator')
        activity_type = request.args.get('type')
        status = request.args.get('status')
        employee = request.args.get('employee')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        result = ActivityHelper.get_all_activities(
            creator=creator,
            activity_type=activity_type,
            status=status,
            employee=employee,
            from_date=from_date,
            to_date=to_date
        )
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in get_all_activities: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/activities/<activity_id>', methods=['GET'])
def get_activity(activity_id):
    """
    Get a specific activity by ID.
    """
    try:
        result = ActivityHelper.get_activity_by_id(activity_id)
        
        if result.get("success"):
            return jsonify(result), 200
        elif result.get("error") == "Activity not found":
            return jsonify(result), 404
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in get_activity: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/activities/user/<email>', methods=['GET'])
def get_user_activities(email):
    """
    Get all activities for a specific user.
    
    Query Parameters:
        - filter: 'all', 'created', or 'joined'
    """
    try:
        filter_type = request.args.get('filter', 'all')
        
        if filter_type not in ['all', 'created', 'joined']:
            return jsonify({
                "success": False,
                "error": "Invalid filter. Must be 'all', 'created', or 'joined'"
            }), 400
        
        result = ActivityHelper.get_user_activities(email, filter_type)
        
        if result.get("success"):
            return jsonify(result), 200
        elif result.get("error") == "User not found":
            return jsonify(result), 404
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in get_user_activities: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/activities/my-activities', methods=['POST'])
def get_my_activities():
    """
    Get all activities for the current user (email passed in body by Gateway).
    
    Expected JSON body:
    {
        "user_email": "user@company.com",  // Set by Gateway from JWT
        "filter": "all"  // Optional: 'all', 'created', or 'joined'
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Request body is required"}), 400
        
        user_email = data.get('user_email')
        if not user_email:
            return jsonify({"success": False, "error": "user_email is required"}), 400
        
        filter_type = data.get('filter', 'all')
        
        result = ActivityHelper.get_user_activities(user_email, filter_type)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in get_my_activities: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# =================== UPDATE OPERATIONS ===================

@app.route('/activities/<activity_id>', methods=['PUT', 'PATCH'])
def update_activity(activity_id):
    """
    Update an existing activity.
    
    Updatable fields:
        - title
        - description
        - type
        - date
        - employees_joined
        - status
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Request body is required"}), 400
        
        result = ActivityHelper.update_activity(
            activity_id=activity_id,
            title=data.get('title'),
            description=data.get('description'),
            activity_type=data.get('type'),
            date=data.get('date'),
            employees_joined=data.get('employees_joined'),
            status=data.get('status')
        )
        
        if result.get("success"):
            return jsonify(result), 200
        elif result.get("error") == "Activity not found":
            return jsonify(result), 404
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in update_activity: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# =================== DELETE OPERATIONS ===================

@app.route('/activities/<activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    """
    Delete an activity.
    """
    try:
        result = ActivityHelper.delete_activity(activity_id)
        
        if result.get("success"):
            return jsonify(result), 200
        elif result.get("error") == "Activity not found":
            return jsonify(result), 404
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in delete_activity: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# =================== PARTICIPANT OPERATIONS ===================

@app.route('/activities/<activity_id>/join', methods=['POST'])
def join_activity(activity_id):
    """
    Add an employee to an activity's participants list.
    
    Expected JSON body:
    {
        "employee_email": "alice@company.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Request body is required"}), 400
        
        employee_email = data.get('employee_email')
        if not employee_email:
            return jsonify({"success": False, "error": "employee_email is required"}), 422
        
        result = ActivityHelper.join_activity(activity_id, employee_email)
        
        if result.get("success"):
            return jsonify(result), 200
        elif "not found" in result.get("error", "").lower():
            return jsonify(result), 404
        elif "already in" in result.get("error", "").lower():
            return jsonify(result), 409
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in join_activity: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/activities/<activity_id>/leave', methods=['POST'])
def leave_activity(activity_id):
    """
    Remove an employee from an activity's participants list.
    
    Expected JSON body:
    {
        "employee_email": "alice@company.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Request body is required"}), 400
        
        employee_email = data.get('employee_email')
        if not employee_email:
            return jsonify({"success": False, "error": "employee_email is required"}), 422
        
        result = ActivityHelper.leave_activity(activity_id, employee_email)
        
        if result.get("success"):
            return jsonify(result), 200
        elif "not found" in result.get("error", "").lower():
            return jsonify(result), 404
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in leave_activity: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/activities/<activity_id>/participants', methods=['GET'])
def get_participants(activity_id):
    """
    Get all participants of an activity.
    
    Query Parameters:
        - include_details: If true, returns full user objects
    """
    try:
        include_details = request.args.get('include_details', 'false').lower() in ['true', '1', 'yes']
        
        result = ActivityHelper.get_activity_participants(activity_id, include_details)
        
        if result.get("success"):
            return jsonify(result), 200
        elif result.get("error") == "Activity not found":
            return jsonify(result), 404
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in get_participants: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/activities/<activity_id>/add-participants', methods=['POST'])
def add_participants(activity_id):
    """
    Add multiple participants to an activity by their emails.
    
    Expected JSON body:
    {
        "emails": ["alice@company.com", "bob@company.com"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Request body is required"}), 400
        
        emails = data.get('emails')
        if not emails or not isinstance(emails, list):
            return jsonify({"success": False, "error": "emails must be a list of email addresses"}), 422
        
        if len(emails) == 0:
            return jsonify({"success": False, "error": "emails list cannot be empty"}), 422
        
        result = ActivityHelper.add_participants_by_emails(activity_id, emails)
        
        return jsonify(result), 200 if result.get("success") else 207  # 207 = Multi-Status
            
    except Exception as e:
        logger.error(f"❌ Error in add_participants: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# =================== UTILITY ENDPOINTS ===================

@app.route('/activities/types', methods=['GET'])
def get_activity_types():
    """Get all valid activity types"""
    return jsonify({
        "success": True,
        "types": ActivityType.get_all_types()
    }), 200


@app.route('/activities/statuses', methods=['GET'])
def get_activity_statuses():
    """Get all valid activity statuses"""
    return jsonify({
        "success": True,
        "statuses": ActivityStatus.get_all_statuses()
    }), 200


# =================== MAIN ===================

if __name__ == '__main__':
    logger.info("🚀 Starting Activity Manager Service on port 7056")
    app.run(host='0.0.0.0', port=7056, debug=False)
