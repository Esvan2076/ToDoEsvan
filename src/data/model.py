from dataclasses import dataclass

@dataclass
class Task:
    id: int
    subject: str
    completed: bool