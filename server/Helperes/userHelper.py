import uuid
from supaBase.supaBase import dataBaseAuth
from modeles.user import User
from testStore.userJson import JsonUserStore
from Helperes.passwordHelper import passwordHelper


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
            return True
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
    def addEmployee(usr, emp):
        if emp not in usr.EmployeesList:
            usr.EmployeesList.append(emp)
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
        data = JsonUserStore("./codes.json")
        for user_id, stored_code in data.items():
            if stored_code == code:
                return user_id
        return None
    
    @static
