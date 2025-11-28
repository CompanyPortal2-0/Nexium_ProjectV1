from typing import List
from meeting import Meeting


class MeetHelper:
    __meetings: List[Meeting] = []
    
    @staticmethod
    def addMeeting(meeting: Meeting) -> None:
        MeetHelper.__meetings.append(meeting)
    
    @staticmethod
    def getMeetings() -> List[Meeting]:
        return MeetHelper.__meetings
    
    @staticmethod
    def addUserToMeeting(meetingID: str, userEmail: str) -> bool:
        for meeting in MeetHelper.__meetings:
            if meeting.getID() == meetingID:
                if userEmail not in meeting.getInvitedEmployeesList():
                    meeting.getInvitedEmployeesList().append(userEmail)
                    return True
                return False  # User already exists
        return False  # Meeting not found
    
    @staticmethod
    def verifyUserInMeeting(meetingID: str, userEmail: str) -> bool:
        for meeting in MeetHelper.__meetings:
            if meeting.getID() == meetingID:
                return userEmail in meeting.getInvitedEmployeesList()
        return False  # Meeting not found
    
    @staticmethod
    def verifyMeetingPassword(meetingID: str, password: str) -> bool:
        for meeting in MeetHelper.__meetings:
            if meeting.getID() == meetingID:
                return meeting.getPassword() == password
        return False  # Meeting not found or password incorrect
    
    @staticmethod
    def getMeetingByID(meetingID: str) -> Meeting:
        for meeting in MeetHelper.__meetings:
            if meeting.getID() == meetingID:
                return meeting
        return None



