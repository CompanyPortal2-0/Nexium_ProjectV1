from typing import List


class MeetHelper :
    def __init__(self):
        self.mettingList: List = []

    def addMetting(self,metting):
        self.mettingList.add(metting)

    def getAllMettings(self):
        return self.mettingList
    
    

