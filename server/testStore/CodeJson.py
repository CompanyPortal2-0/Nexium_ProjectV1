
import json
from typing import Optional

class JsonManagerCode :
    def __init__(self,filePath):
        self.filepath = filePath
        self._ensure_file()

    def set_code(self, code: str, managerId: str):
        data = self._read()
        data[code] = managerId
        self._write(data)

    def _ensure_file(self):
        try:
            with open(self.filepath, 'r') as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)


    def get_code(self, code: str) -> Optional[str]:
        data = self._read()
        return data.get(code)

    def _read(self):
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def _write(self, data):
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)