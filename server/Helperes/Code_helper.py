import random
import string

from testStore.CodeJson import JsonManagerCode
from modeles.code import Code

class codeHelper:
    @staticmethod
    def generateCode():


        length = 6
        characters = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(characters) for _ in range(length))
        return code

    @staticmethod
    def saveCode(Rcode,manager_mail):

        JMC=JsonManagerCode("./codeJson.json")
        JMC.set_code(Rcode, manager_mail)
        return Rcode

    @staticmethod
    def getManagerMAILByCode( code):
        JMC=JsonManagerCode("./codeJson.json")
        managerId = JMC.get_code(code)
        return managerId







