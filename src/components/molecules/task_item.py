import flet as ft
from data.model import Task
from data import crud
from utils.theme import AppColors

class TaskItem(ft.Row):
    def __init__(self, task: Task, on_delete_callback, on_status_change_callback):
        super().__init__()
        self.task = task
        self.on_delete_callback = on_delete_callback
        self.on_status_change_callback = on_status_change_callback
        
        # Alignment settings
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

        # Checkbox for status
        self.checkbox = ft.Checkbox(
            label=self.task.subject,
            value=self.task.completed,
            on_change=self.status_changed,
            active_color=AppColors.SAFE
        )

        self.delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE, 
            icon_color=AppColors.DANGER,
            on_click=self.delete_clicked
        )

        # Add controls to the Row
        self.controls = [self.checkbox, self.delete_btn]

    def status_changed(self, e):
        # Update local object state
        self.task.completed = self.checkbox.value
        # Update Database
        crud.update_task_status(self.task.id, self.task.completed)
        if self.on_status_change_callback:
            self.on_status_change_callback()
        print(f"Update: Task {self.task.id} is now {self.task.completed}")

    def delete_clicked(self, e):
        # Notify parent to handle deletion (visual and DB)
        self.on_delete_callback(self)
        print(f"Delete: Task {self.task.id} was deleted")