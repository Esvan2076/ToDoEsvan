import flet as ft
from components.molecules.task_item import TaskItem
from utils.theme import AppColors

class TodoList(ft.Column):
    def __init__(self, on_delete_task, on_status_change):
        super().__init__()
        self.on_delete_task = on_delete_task
        self.on_status_change = on_status_change
        self.expand = True # Que ocupe todo el espacio disponible
        self.scroll = ft.ScrollMode.AUTO # Scroll automático si hay muchas tareas

    def show_loading(self):
        self.controls.clear()
        if self.page:
            self.update()

    def render_tasks(self, tasks):
        """Paso 3 y 4: Recibir datos y decidir si mostrar lista o empty"""
        self.controls.clear() # Quitamos los esqueletos grises

        if not tasks:
            # Paso 3: Empty State
            self.controls.append(
                ft.Container(
                    content=ft.Text("Nothing here!", color=AppColors.HINT_TEXT, italic=True),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            # Paso 4: Renderizar tareas reales
            for task in tasks:
                item = TaskItem(
                    task, 
                    on_delete_callback=self.on_delete_task,
                    on_status_change_callback=self.on_status_change
                )
                self.controls.append(item)
        
        if self.page:
            self.update()