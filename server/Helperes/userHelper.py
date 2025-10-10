from modeles.user import User

class userHelper : 
    def getUserByEmail(email: str) -> User:
        # Simulate a user lookup
        return User(Email=email, FirstName="John", LastName="Doe")
    def CreateUser(Email, FirstName, LastName,  DateOfBirth,  Address , password) -> bool:
        ID = 55
        newUser = User(Email, FirstName, LastName, ID, DateOfBirth, Address)

        return True


