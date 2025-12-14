from __future__ import annotations  # permite usar tipos definidos más abajo (como Task)

from typing import List

from todoesvan.data.database import get_db_connection
from todoesvan.data.model import Task


class TaskRepository:
    def create(self, subject: str) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO task (subject) VALUES (%s);",
                    (subject,),
                )

    def get_tasks(self, completed: bool) -> List[Task]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, subject, completed
                    FROM task
                    WHERE completed = %s
                    ORDER BY created_at DESC;
                    """,
                    (completed,),
                )
                rows = cur.fetchall()
        return [Task(id=row[0], subject=row[1], completed=row[2]) for row in rows]

    def set_completed(self, task_id: int, completed: bool) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE task SET completed = %s WHERE id = %s;",
                    (completed, task_id),
                )

    def delete(self, task_id: int) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM task WHERE id = %s;",
                    (task_id,),
                )
