from typing import Callable, List, Optional, Set

import flet as ft

from todoesvan.components.molecules.task_item import TaskItem
from todoesvan.data.model import Task
from todoesvan.utils.theme import AppColors


class TodoList(ft.Column):
    def __init__(
        self,
        on_delete_task: Callable[[int], None],
        on_status_change: Callable[[int, bool], None],
        on_update_subject: Callable[[int, str], None],
    ):
        super().__init__()
        self.on_delete_task = on_delete_task
        self.on_status_change = on_status_change
        self.on_update_subject = on_update_subject

        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.scrollbar = False

    def show_loading(self) -> None:
        self.controls.clear()
        if self.page:
            self.update()

    def render_tasks(
        self,
        tasks: List[Task],
        pending_ids: Optional[Set[int]] = None,
        refreshing: bool = False,
    ) -> None:
        pending_ids = pending_ids or set()
        self.controls.clear()

        if refreshing and not tasks:
            self.controls.append(
                ft.Container(
                    content=ft.Text("Loading...", color=AppColors.TEXT_MUTED, italic=True),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
        elif not tasks:
            self.controls.append(
                ft.Container(
                    content=ft.Text("Nothing here!", color=AppColors.TEXT_MUTED, italic=True),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
        else:
            for task in tasks:
                self.controls.append(
                    TaskItem(
                        task=task,
                        pending=(task.id in pending_ids),
                        on_delete=self.on_delete_task,
                        on_toggle=self.on_status_change,
                        on_update_subject=self.on_update_subject,
                    )
                )

        if self.page:
            self.update()
