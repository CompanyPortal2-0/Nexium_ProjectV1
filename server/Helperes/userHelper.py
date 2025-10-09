from modeles.user import User

class userHelper : 
    def getUserByEmail(email: str) -> User:
        # Simulate a user lookup
        return User(Email=email, FirstName="John", LastName="Doe")


