
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

        
