from supaBase.supaBase import dataBaseAuth
import json

class authHelper : 
    def __init__(self,database : dataBaseAuth):
        self.authenticater=database
    
    def CreateUser(self,Email,password):
        try:
            print("result : ")
            result = self.authenticater.createUser(Email,password)
            print("result type : ", type(result))
            if(result is not None):
                result = json.loads(result)
                session = (result.get("session", {}))
                user = (result.get("user", {}))
                print("user : ")
                print(user)
                print("seesion : ")
                print(session)
                return json.dumps({"Token":session.get("access_token"),"id":user.get("id")})
        except Exception as e:
            print(f"Auth creation error: {e}")
            return None
        
    
    def login (self,Email,password):
        try:
            print("email : ",Email)
            print("passwor : " , password)
            result = self.authenticater.login(Email,password)
            print("result type : ", type(result))
            if(result is not None):
                result = json.loads(result)
                session = (result.get("session", {}))
                user = (result.get("user", {}))
                print("user : ")
                print(user)
                print("seesion : ")
                print(session)
                return json.dumps({"Token":session.get("access_token"),"id":user.get("id")})
        except Exception as e:
            print(f"Auth login error: {e}")
            return False
        
    def deleteUser(self,userId):
        try:
            result = self.authenticater.delUser(userId)
            if(result is not None):
                result = json.loads(result)
                return json.dumps({"status":"user deleted"})
        except Exception as e :
            print(f"matna7ach user :{userId} ")