from pydantic import BaseModel, Field
from typing import List, Dict

class StudentPerformance(BaseModel):
    email: str
    name: str
    age: int
    history: List[Dict] = Field(default_factory=list) 