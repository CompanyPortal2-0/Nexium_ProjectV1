import bcrypt
from modeles.passwordSecuirity import passwordSecurity
from testStore import json_user_password_store
from testStore.json_user_password_store import JsonUserPasswordStore


class passwordHelper:


    @staticmethod
    def EncrpytingPassword(password):
        """Hash password using bcrypt with automatic salt generation"""
        # Convert password to bytes and hash it
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def CompareHashPasswordandPassword(hashedPassword, plainPassword):
        """Compare hashed password with plain password using bcrypt"""
        try:
            return bcrypt.checkpw(plainPassword.encode('utf-8'), hashedPassword.encode('utf-8'))
        except Exception as e:
            print(f"Password comparison error: {e}")
            return False

    @staticmethod
    def assignPasswordToUser(userId, password):
        jsonPass= JsonUserPasswordStore("./passJson.json")
        encryptedPassword = passwordHelper.EncrpytingPassword(password)
        ##SecuirityClass = passwordSecurity(encryptedPassword, userId)
        jsonPass.set_password(userId, encryptedPassword)


    @staticmethod
    def isPasswordTrueForUser(userid, password):
        #get hashed password from db by user id


        hashedPassword = passwordHelper.getPasswordForUser(userid)
        print(hashedPassword)
        if hashedPassword is None:
            return False
        return passwordHelper.CompareHashPasswordandPassword(hashedPassword, password)

    @staticmethod
    def getPasswordForUser(userid):
        #get hashed password from db by user id
        json_user_password_store = JsonUserPasswordStore("./passJson.json")
        hashedPassword = json_user_password_store.get_password(userid)
        # Replace with actual retrieval logic
        return hashedPassword