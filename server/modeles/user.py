from __future__ import annotations
from dataclasses import dataclass

from modeles.department import Department
from modeles.role import ROLE


class User:


    def __init__(self,Email=None, FirstName=None, LastName=None,  ID=None,DateOfBirth=None,  Address=None):
        self.ID = ID
        self.FirstName = FirstName
        self.LastName = LastName
        self.DateOfBirth = DateOfBirth
        self.Email = Email
        self.Address = Address
        self.EmployeesList = []
        self.Department = None
        self.Role = ROLE.GUEST

    def getId(self):
        return self.ID

    def setId(self, id_value):
        self.ID = id_value

    def getFirstName(self):
        return self.FirstName

    def setFirstName(self, first_name):
        self.FirstName = first_name

    def getLastName(self):
        return self.LastName

    def setLastName(self, last_name):
        self.LastName = last_name

    def getDateOfBirth(self):
        return self.DateOfBirth

    def setDateOfBirth(self, dob):
        self.DateOfBirth = dob

    def getEmail(self):
        return self.Email

    def setEmail(self, email):
        self.Email = email

    def getAddress(self):
        return self.Address

    def setAddress(self, address):
        self.Address = address

    def getEmployeesList(self):
        return self.EmployeesList

    def setEmployeesList(self, employees):
        self.EmployeesList = list(employees)
    def getDepartment(self):
        return self.Department

    def setDepartment(self, department: Department):
        self.Department = department

    def getRole(self):
        return self.Role

    def setRole(self, role: ROLE):
        self.Role = role
    def __str__(self):
        return "User(ID=%r, FirstName=%r, LastName=%r)" % (self.ID, self.FirstName, self.LastName)
