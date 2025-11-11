
import secrets
import string
from modeles.meet import Meeting
from testStore.meetJson import JsonMeetingStore

class meetHelper :
    @staticmethod
    def create_meet(title,object,Description,CreterMail):
        saver = JsonMeetingStore()
        ID = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        meet = Meeting (
            ID,
            title,
            object,
            ID,
            "/log.log",
            Description,
            [],
            CreterMail
        )
        saver.add_meeting(meet)

        return meet
    
    @staticmethod
    def joinMeet(userMAil,meetID):
        try:
            saver = JsonMeetingStore()

            # Get the meeting by ID
            meeting = saver.get_meeting_by_id(meetID)

            if meeting is None:
                print(f"Meeting with ID {meetID} not found")
                return False

            # Check if user is already in the invited list
            invited_list = meeting.getInvitedEmployeesList()
            if (userMAil in invited_list) or (userMAil == meeting.getCreator()):
                print(f"User {userMAil} is already invited to this meeting")
                return True

            # Add user to the meeting using the JsonMeetingStore method
            success = saver.add_employee_to_meeting(meetID, userMAil)

            if success:
                print(f"User {userMAil} successfully added to meeting {meetID}")
                return True
            else:
                print(f"Failed to add user {userMAil} to meeting {meetID}")
                return False
            
        except Exception as e:
            print(f"Error joining meeting: {e}")
            return False

        
