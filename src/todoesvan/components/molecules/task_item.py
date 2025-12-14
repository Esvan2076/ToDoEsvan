from typing import Callable

import flet as ft

from todoesvan.data.model import Task
from todoesvan.utils.theme import AppColors


class TaskItem(ft.Row):
    def __init__(
        self,
        task: Task,
        on_delete: Callable[[int], None],
        on_toggle: Callable[[int, bool], None],
    ):
        super().__init__()
        self.task = task
        self.on_delete = on_delete
        self.on_toggle = on_toggle

        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

        self.checkbox = ft.Checkbox(
            value=self.task.completed,
            on_change=self._status_changed,
            active_color=AppColors.INTENT_POSITIVE,
        )

        self.title = ft.Text(
            value=self.task.subject,
            size=16,
            color=AppColors.TEXT_PRIMARY,
            max_lines=3,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.left = ft.Row(
            controls=[self.checkbox, ft.Container(content=self.title, expand=True)],
            spacing=10,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color=AppColors.INTENT_DESTRUCTIVE,
            on_click=self._delete_clicked,
        )

        self.controls = [self.left, self.delete_btn]

    def _status_changed(self, e: ft.ControlEvent):
        if self.on_toggle:
            self.on_toggle(self.task.id, self.checkbox.value)

    def _delete_clicked(self, e: ft.ControlEvent):
        if self.on_delete:
            self.on_delete(self.task.id)
