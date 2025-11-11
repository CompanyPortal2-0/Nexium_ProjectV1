import json
from typing import List, Optional
from modeles.meet import Meeting
import os

class JsonMeetingStore:
    def __init__(self, filepath: str = "./meetings.json"):
        """
        Initialize the JSON Meeting Store
        
        Args:
            filepath: Path to the JSON file storing meetings
        """
        self.filepath = filepath
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the JSON file if it doesn't exist"""
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f, indent=2)
    
    def add_meeting(self, meeting: Meeting) -> bool:
        """
        Add a new meeting to the JSON store
        
        Args:
            meeting: Meeting object to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read existing meetings
            with open(self.filepath, 'r') as f:
                meetings = json.load(f)
            
            # Check if meeting already exists
            if meeting.getID() in meetings:
                print(f"Meeting with ID {meeting.getID()} already exists")
                return False
            
            # Add new meeting
            meetings[meeting.getID()] = meeting.to_dict()
            
            # Write back to file
            with open(self.filepath, 'w') as f:
                json.dump(meetings, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding meeting: {e}")
            return False
    
    def get_meeting_by_id(self, meeting_id: str) -> Optional[Meeting]:
        """
        Get a meeting by its ID
        
        Args:
            meeting_id: ID of the meeting to retrieve
            
        Returns:
            Meeting object or None if not found
        """
        try:
            with open(self.filepath, 'r') as f:
                meetings = json.load(f)
            
            if meeting_id in meetings:
                return Meeting.from_dict(meetings[meeting_id])
            return None
        except Exception as e:
            print(f"Error getting meeting: {e}")
            return None
    
    def get_all_meetings(self) -> List[Meeting]:
        """
        Get all meetings from the store
        
        Returns:
            List of Meeting objects
        """
        try:
            with open(self.filepath, 'r') as f:
                meetings = json.load(f)
            
            return [Meeting.from_dict(data) for data in meetings.values()]
        except Exception as e:
            print(f"Error getting all meetings: {e}")
            return []
    
    def get_meetings_by_creator(self, creator_email: str) -> List[Meeting]:
        """
        Get all meetings created by a specific user
        
        Args:
            creator_email: Email of the creator
            
        Returns:
            List of Meeting objects
        """
        all_meetings = self.get_all_meetings()
        return [m for m in all_meetings if m.getCreator() == creator_email]
    
    def get_meetings_for_employee(self, employee_id: str) -> List[Meeting]:
        """
        Get all meetings where an employee is invited
        
        Args:
            employee_id: ID or email of the employee
            
        Returns:
            List of Meeting objects
        """
        all_meetings = self.get_all_meetings()
        return [m for m in all_meetings if employee_id in m.getInvitedEmployeesList()]
    
    def update_meeting(self, meeting: Meeting) -> bool:
        """
        Update an existing meeting
        
        Args:
            meeting: Meeting object with updated data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.filepath, 'r') as f:
                meetings = json.load(f)
            
            if meeting.getID() not in meetings:
                print(f"Meeting with ID {meeting.getID()} not found")
                return False
            
            # Update meeting
            meetings[meeting.getID()] = meeting.to_dict()
            
            # Write back to file
            with open(self.filepath, 'w') as f:
                json.dump(meetings, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating meeting: {e}")
            return False
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """
        Delete a meeting by ID
        
        Args:
            meeting_id: ID of the meeting to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.filepath, 'r') as f:
                meetings = json.load(f)
            
            if meeting_id not in meetings:
                print(f"Meeting with ID {meeting_id} not found")
                return False
            
            # Remove meeting
            del meetings[meeting_id]
            
            # Write back to file
            with open(self.filepath, 'w') as f:
                json.dump(meetings, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error deleting meeting: {e}")
            return False
    
    def add_employee_to_meeting(self, meeting_id: str, employee_id: str) -> bool:
        """
        Add an employee to a meeting's invitation list
        
        Args:
            meeting_id: ID of the meeting
            employee_id: ID or email of the employee to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        meeting = self.get_meeting_by_id(meeting_id)
        if meeting is None:
            return False
        
        invited_list = meeting.getInvitedEmployeesList()
        if employee_id not in invited_list:
            invited_list.append(employee_id)
            meeting.setInvitedEmployeesList(invited_list)
            return self.update_meeting(meeting)
        return True
    
    def remove_employee_from_meeting(self, meeting_id: str, employee_id: str) -> bool:
        """
        Remove an employee from a meeting's invitation list
        
        Args:
            meeting_id: ID of the meeting
            employee_id: ID or email of the employee to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        meeting = self.get_meeting_by_id(meeting_id)
        if meeting is None:
            return False
        
        invited_list = meeting.getInvitedEmployeesList()
        if employee_id in invited_list:
            invited_list.remove(employee_id)
            meeting.setInvitedEmployeesList(invited_list)
            return self.update_meeting(meeting)
        return True
    
    def get_meeting_count(self) -> int:
        """
        Get total number of meetings
        
        Returns:
            int: Number of meetings
        """
        try:
            with open(self.filepath, 'r') as f:
                meetings = json.load(f)
            return len(meetings)
        except Exception as e:
            print(f"Error getting meeting count: {e}")
            return 0