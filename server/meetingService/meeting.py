from typing import List

class Meeting:
    def __init__(self):
        self.__ID: str = ""
        self.__Title: str = ""
        self.__Object: str = ""
        self.__InvitationLink: str = ""
        self.__LogPath: str = ""
        self.__Description: str = ""
        self.__InvitedEmployeesList: List = []
        self.__CreatedAt: str = ""
        
    
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
