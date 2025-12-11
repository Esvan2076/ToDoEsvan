from data.database import get_db_connection
from data.model import Task # We will update the model below

def create_task(subject: str):
    """Inserts a new task into the database."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "INSERT INTO task (subject) VALUES (%s);"
        cursor.execute(query, (subject,))
        conn.commit()
        cursor.close()
        conn.close()

def get_tasks(completed_status: bool):
    """
    Fetches tasks filtered by status via SQL.
    True = Completed, False = Active
    """
    conn = get_db_connection()
    tasks = []
    if conn:
        cursor = conn.cursor()

        query = "SELECT id, subject, completed FROM task WHERE completed = %s ORDER BY created_at DESC;"
        cursor.execute(query, (completed_status,))
        rows = cursor.fetchall()
        
        for row in rows:
            tasks.append(Task(id=row[0], subject=row[1], completed=row[2]))
            
        cursor.close()
        conn.close()
    return tasks

def update_task_status(task_id: int, completed: bool):
    """Updates the completed status of a task."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "UPDATE task SET completed = %s WHERE id = %s;"
        cursor.execute(query, (completed, task_id))
        conn.commit()
        cursor.close()
        conn.close()

def delete_task(task_id: int):
    """Deletes a task by ID."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "DELETE FROM task WHERE id = %s;"
        cursor.execute(query, (task_id,))
        conn.commit()
        cursor.close()
        conn.close()