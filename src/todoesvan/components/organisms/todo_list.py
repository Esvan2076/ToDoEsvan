from typing import Callable, List

import flet as ft

from todoesvan.components.molecules.task_item import TaskItem
from todoesvan.data.model import Task
from todoesvan.utils.theme import AppColors


class TodoList(ft.Column):
    def __init__(
        self,
        on_delete_task: Callable[[int], None],
        on_status_change: Callable[[int, bool], None],
    ):
        super().__init__()

        self.on_delete_task = on_delete_task
        self.on_status_change = on_status_change

        # Layout behavior
        self.expand = True                     # Take all available vertical space
        self.scroll = ft.ScrollMode.AUTO       # Enable scrolling for long lists

    def show_loading(self) -> None:
        self.controls.clear()

        if self.page:
            self.update()

    def render_tasks(self, tasks: List[Task]) -> None:
        # Remove previous items
        self.controls.clear()

        if not tasks:
            # Empty state
            self.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nothing here!",
                        color=AppColors.TEXT_MUTED,
                        italic=True,
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
        else:
            # Render each task item
            for task in tasks:
                item = TaskItem(
                    task=task,
                    on_delete=self.on_delete_task,      # expects task_id
                    on_toggle=self.on_status_change,    # expects (task_id, completed)
                )
                self.controls.append(item)

        if self.page:
            self.update()
