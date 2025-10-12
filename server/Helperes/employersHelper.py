from modeles.employer import Employer

class EmployerHelper:
    @staticmethod
    def getEmployerByEmail(email: str) -> Employer:

        return Employer()

    @staticmethod
    def CreateEmployer(Email, FirstName, LastName,  DateOfBirth,  Address , password, Department, Role) -> bool:
        ID = 55
        newEmployer = Employer()
        newEmployer.Email = Email
        newEmployer.FirstName = FirstName
        newEmployer.LastName = LastName
        newEmployer.ID = ID
        newEmployer.DateOfBirth = DateOfBirth
        newEmployer.Address = Address
        newEmployer.Department = Department
        newEmployer.Role = Role

        return True

    @staticmethod
    def getAllEmployers():
        employers = [
            # njibo employers ml base de donner
            ]
        return employers