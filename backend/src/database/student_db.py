import orjson
from pathlib import Path
from typing import Optional
from ..models.student_models import StudentPerformance

class StudentDB:
    def __init__(self, path: Path):
        self.path = path
        self._ensure_file()
        self._load()

    def _ensure_file(self):
        if not self.path.exists():
            self.path.write_bytes(orjson.dumps({}))

    def _load(self):
        try:
            content = self.path.read_bytes()
            if not content:
                self.data = {}
            else:
                self.data = orjson.loads(content)
        except orjson.JSONDecodeError:
            self.data = {}

    def save(self):
        self.path.write_bytes(orjson.dumps(self.data))

    def get_student(self, email: str) -> Optional[StudentPerformance]:
        self._load()
        if email in self.data:
            return StudentPerformance(**self.data[email])
        return None

    def upsert_student(self, student: StudentPerformance):
        self.data[student.email] = student.model_dump()
        self.save()
        print(f"[LOG] Saved/Updated student: {student.email} | Data: {student.model_dump()}") 