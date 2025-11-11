
import secrets
import string
from modeles.meet import Meeting
from testStore.meetJson import JsonMeetingStore

class meetHelper :
    @staticmethod
    def create_meet(title,object,Description,CreterMail):
        """
        Create a new meeting
        
        Args:
            title: Meeting title
            object: Meeting object/subject
            Description: Meeting description
            CreterMail: Email of the creator
            
        Returns:
            Meeting object if successful, None otherwise
        """
        try:
            saver = JsonMeetingStore()
            ID = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            
            meet = Meeting (
                ID,
                title,
                object,
                ID,  # InvitationLink is same as ID
                "/log.log",
                Description,
                [],
                CreterMail
            )
            saver.add_meeting(meet)
            return meet
        except Exception as e:
            print(f"Error creating meeting: {e}")
            return None
    
    @staticmethod
    def get_meeting(meeting_id):
        """
        Get a meeting by its ID
        
        Args:
            meeting_id: ID of the meeting
            
        Returns:
            Meeting object if found, None otherwise
        """
        try:
            saver = JsonMeetingStore()
            return saver.get_meeting_by_id(meeting_id)
        except Exception as e:
            print(f"Error getting meeting: {e}")
            return None
    
    @staticmethod
    def get_user_meetings(user_email):
        """
        Get all meetings for a specific user (created by or invited to)
        
        Args:
            user_email: Email of the user
            
        Returns:
            List of Meeting objects
        """
        try:
            saver = JsonMeetingStore()
            all_meetings = saver.get_all_meetings()
            
            # Filter meetings where user is creator or invited
            user_meetings = []
            for meeting in all_meetings:
                if (meeting.getCreator() == user_email or 
                    user_email in meeting.getInvitedEmployeesList()):
                    user_meetings.append(meeting)
            
            return user_meetings
        except Exception as e:
            print(f"Error getting user meetings: {e}")
            return []
    
    @staticmethod
    def is_user_in_meeting(user_email, meeting_id):
        """
        Check if a user is authorized to join a meeting (creator or invited)
        
        Args:
            user_email: Email of the user
            meeting_id: ID of the meeting
            
        Returns:
            True if user is authorized, False otherwise
        """
        try:
            meeting = meetHelper.get_meeting(meeting_id)
            if meeting is None:
                return False
            
            return (meeting.getCreator() == user_email or 
                    user_email in meeting.getInvitedEmployeesList())
        except Exception as e:
            print(f"Error checking user authorization: {e}")
            return False
    
    @staticmethod
    def joinMeet(userMail, meetID):
        """
        Add a user to a meeting's invited list
        
        Args:
            userMail: Email of the user
            meetID: ID of the meeting
            
        Returns:
            True if successful, False otherwise
        """
        try:
            saver = JsonMeetingStore()

            # Get the meeting by ID
            meeting = saver.get_meeting_by_id(meetID)

            if meeting is None:
                print(f"Meeting with ID {meetID} not found")
                return False

            # Check if user is already in the invited list or is the creator
            invited_list = meeting.getInvitedEmployeesList()
            if (userMail in invited_list) or (userMail == meeting.getCreator()):
                print(f"User {userMail} is already invited to this meeting")
                return True

            # Add user to the meeting using the JsonMeetingStore method
            success = saver.add_employee_to_meeting(meetID, userMail)

            if success:
                print(f"User {userMail} successfully added to meeting {meetID}")
                return True
            else:
                print(f"Failed to add user {userMail} to meeting {meetID}")
                return False
            
        except Exception as e:
            print(f"Error joining meeting: {e}")
            return False
    
    @staticmethod
    def delete_meeting(meeting_id, user_email):
        """
        Delete a meeting (only creator can delete)
        
        Args:
            meeting_id: ID of the meeting
            user_email: Email of the user attempting to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            saver = JsonMeetingStore()
            meeting = saver.get_meeting_by_id(meeting_id)
            
            if meeting is None:
                print(f"Meeting with ID {meeting_id} not found")
                return False
            
            # Only creator can delete
            if meeting.getCreator() != user_email:
                print(f"User {user_email} is not authorized to delete meeting {meeting_id}")
                return False
            
            return saver.delete_meeting(meeting_id)
        except Exception as e:
            print(f"Error deleting meeting: {e}")
            return False

        
