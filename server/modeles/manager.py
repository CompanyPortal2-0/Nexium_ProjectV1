from .employer import Employer


class Manager(Employer):
    """Manager with a simple EmployeesList attribute (list of Employer)."""

    def __init__(self):
        super().__init__()
        self.EmployeesList = []

    def getEmployeesList(self):
        return self.EmployeesList

    def setEmployeesList(self, employees):
        self.EmployeesList = list(employees)

    def addEmployee(self, emp):
        if emp not in self.EmployeesList:
            self.EmployeesList.append(emp)

    def removeEmployee(self, emp):
        if emp in self.EmployeesList:
            self.EmployeesList.remove(emp)

    def __repr__(self):
        return "Manager(ID=%r, employees_count=%d)" % (self.ID, len(self.EmployeesList))
