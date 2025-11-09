import uuid
from supaBase.supaBase import dataBaseAuth
from modeles.user import User
from testStore.userJson import JsonUserStore
from Helperes.passwordHelper import passwordHelper
from modeles.role import ROLE


class userHelper :

    @staticmethod
    def getUserByEmail(email: str) -> User:
        AllUseres = JsonUserStore("./userJson.json").get_all_users()
        for user in AllUseres:
            if user.Email == email:
                return user
        return None

    @staticmethod
    def CreateUser(Email, FirstName, LastName,  DateOfBirth,  Address , password) -> bool:
        try:
            Jstore = JsonUserStore("./userJson.json")
            ID = str(uuid.uuid4())
            # Pass an empty list for EmployeesList
            newUser = User(Email, FirstName, LastName, ID, DateOfBirth, Address, EmployeesList=[])
            Jstore.add_user(newUser)
            passwordHelper.assignPasswordToUser(newUser.ID, password)
            return True , newUser
        except Exception as e:
            print(f"Create user error: {e}")
            return False

    

    @staticmethod
    def getAllUsers(type) :
        users = JsonUserStore("./userJson.json").get_all_users()
        if type is not None :
            users = [user for user in users if user.Role == type]
        return users

    
    @staticmethod
    def removeEmployee(user, emp):
        if emp in user.EmployeesList:
            user.EmployeesList.remove(emp)

    @staticmethod
    def assignCodeToManager(manager : User,code):
        codes = JsonUserStore("./codes.json")
        codes.codeToMangaer(manager,code)
    @staticmethod
    def getManagerFromCode(code):
        data = JsonUserStore("./codes.json").get_all_code()
        for item in data:
            for user_id, stored_code in item.items():
                if stored_code == code:
                    return user_id
        return None
    
    @staticmethod
    def addemployerTomanager(manager : User,user : User):
        manager.EmployeesList.append(user)
        try :
            JsonUserStore("./userJson").add_user(manager)
            return True
        except Exception as e:
            return False
