from typing import List

from todoesvan.data.model import Task
from todoesvan.data.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def add_task(self, subject: str) -> None:
        title = (subject or "").strip()
        if not title:
            raise ValueError("Task cannot be empty.")
        self.repo.create(title)

    def get_tasks(self, completed: bool) -> List[Task]:
        return self.repo.get_tasks(completed)

    def toggle_completed(self, task_id: int, completed: bool) -> None:
        self.repo.set_completed(task_id, completed)

    def delete_task(self, task_id: int) -> None:
        self.repo.delete(task_id)
