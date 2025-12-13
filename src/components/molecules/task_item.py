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

        # Row layout
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

        # Checkbox (sin label)
        self.checkbox = ft.Checkbox(
            value=self.task.completed,
            on_change=self.status_changed,
            active_color=AppColors.SAFE
        )

        # Texto de tarea (más grande + wrap hasta 3 líneas)
        self.title = ft.Text(
            value=self.task.subject,
            size=16,                       # letra más grande
            color=AppColors.TEXT,
            max_lines=3,                   # límite 3 renglones
            overflow=ft.TextOverflow.ELLIPSIS,  # ... si se pasa
        )

        # Bloque izquierdo: checkbox + texto con separación
        self.left = ft.Row(
            controls=[
                self.checkbox,
                ft.Container(content=self.title, expand=True),
            ],
            expand=True,                   # ✅ ocupa el ancho disponible y permite wrap
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color=AppColors.DANGER,
            on_click=self.delete_clicked
        )

        self.controls = [self.left, self.delete_btn]

    def status_changed(self, e):
        self.task.completed = self.checkbox.value
        crud.update_task_status(self.task.id, self.task.completed)
        if self.on_status_change_callback:
            self.on_status_change_callback()

    def delete_clicked(self, e):
        self.on_delete_callback(self)
