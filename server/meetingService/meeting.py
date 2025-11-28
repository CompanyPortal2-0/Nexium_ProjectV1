from typing import List
import uuid
from datetime import datetime

class Meeting:
    def __init__(self, title: str = "", obj: str = "", description: str = "", invited_employees: List[str] = None, password: str = ""):
        self.__ID: str = str(uuid.uuid4())
        self.__Title: str = title
        self.__Object: str = obj
        self.__InvitationLink: str = f"http://localhost:7053/room/{self.__ID}"
        self.__LogPath: str = ""
        self.__Description: str = description
        self.__InvitedEmployeesList: List = invited_employees if invited_employees else []
        self.__CreatedAt: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__Password: str = password
        
    
    def getID(self) -> str:
        return self.__ID
    
    def setID(self, ID: str) -> None:
        self.__ID = ID
    
    def getTitle(self) -> str:
        return self.__Title
    
    def setTitle(self, Title: str) -> None:
        self.__Title = Title
    
    def getObject(self) -> str:
        return self.__Object
    
    def setObject(self, Object: str) -> None:
        self.__Object = Object
    
    def getInvitationLink(self) -> str:
        return self.__InvitationLink
    
    def setInvitationLink(self, InvitationLink: str) -> None:
        self.__InvitationLink = InvitationLink
    
    def getLogPath(self) -> str:
        return self.__LogPath
    
    def setLogPath(self, LogPath: str) -> None:
        self.__LogPath = LogPath
    
    def getDescription(self) -> str:
        return self.__Description
    
    def setDescription(self, Description: str) -> None:
        self.__Description = Description
    
    def getInvitedEmployeesList(self) -> List:
        return self.__InvitedEmployeesList
    
    def setInvitedEmployeesList(self, InvitedEmployeesList: List) -> None:
        self.__InvitedEmployeesList = InvitedEmployeesList
    
    def getCreatedAt(self) -> str:
        return self.__CreatedAt
    
    def getPassword(self) -> str:
        return self.__Password
    
    def setPassword(self, Password: str) -> None:
        self.__Password = Password
