
from .user import User
from .department import Department
from .role import ROLE


class Employer(User):
    def __init__(self):
        super().__init__()
        self.Department = None  
        self.Role = ROLE.GUEST

    def getID(self):
        return self.ID
    def setID(self, id_value):
        self.ID = id_value

    def getDepartment(self):
        return self.Department

    def setDepartment(self, department: Department):
        self.Department = department

    def getRole(self):
        return self.Role

    def setRole(self, role: ROLE):
        self.Role = role

    def __str__(self):
        return "Employer(ID=%r, role=%r, department=%r)" % (self.ID, self.Role, self.Department)
