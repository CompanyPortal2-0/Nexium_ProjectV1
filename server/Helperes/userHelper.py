from modeles.user import User

class userHelper :
    @staticmethod
    def getUserByEmail(email: str) -> User:
        # Simulate a user lookup
        return User(Email=email, FirstName="John", LastName="Doe")

    @staticmethod
    def CreateUser(Email, FirstName, LastName,  DateOfBirth,  Address , password) -> bool:
        ID = 55
        newUser = User(Email, FirstName, LastName, ID, DateOfBirth, Address)

        return True

    @staticmethod
    def getAllUsers() :
        users = [
            # njibo users ml base de donner
            ]
        return users

    @staticmethod
    def addEmployee(usr, emp):
        if emp not in usr.EmployeesList:
            usr.EmployeesList.append(emp)
    @staticmethod
    def removeEmployee(user, emp):
        if emp in user.EmployeesList:
            user.EmployeesList.remove(emp)



