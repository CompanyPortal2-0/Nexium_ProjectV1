from supaBase.supaBase import dataBaseAuth



class authHelper : 
    def __init__(self,database : dataBaseAuth):
        self.authenticater=database
    
    def CreateUser(self,Email,password) -> bool:
        
        return self.authenticater.createUser(Email,password)
        
    
    def login (self,Email,password) -> bool:
         return self.authenticater.login(Email,password)
