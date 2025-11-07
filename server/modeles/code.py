class Code :
    def __init__(self, code_id, managerId):
        self.code_id = code_id
        self.managerId = managerId

    def get_managerId(self):
        return self.managerId

    def get_code(self):
        return self.code_id

    def to_dict(self):
        return {
            "code_id": self.code_id,
            "managerId": self.managerId
        }
    @classmethod
    def from_dict(cls, data):
        return cls(
            code_id=data.get("code_id"),
            managerId=data.get("managerId")
        )




    def __repr__(self):
        return f"Code(code_id={self.code_id}, managerId={self.managerId})"