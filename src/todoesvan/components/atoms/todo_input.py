from typing import Callable

import flet as ft

from todoesvan.utils.theme import AppColors, UISizes


class TodoInput(ft.Column):
    def __init__(self, on_submit_action: Callable[[ft.ControlEvent], None]):
        super().__init__()
        self.expand = True
        self.spacing = 4

        self._field = ft.TextField(
            on_submit=on_submit_action,
            on_change=self._on_change,
            hint_text="What needs to be done?",
            hint_style=ft.TextStyle(color=AppColors.TEXT_MUTED),
            text_style=ft.TextStyle(color=AppColors.TEXT_PRIMARY),
            height=UISizes.INPUT_HEIGHT,
            border_color=AppColors.BORDER_DEFAULT,
            focused_border_color=AppColors.ACCENT,
            max_length=50,
        )

        self._normal_border_color = AppColors.BORDER_DEFAULT
        self._normal_focused_border_color = AppColors.ACCENT

        self._error = ft.Text(
            value="",
            color=AppColors.INTENT_DESTRUCTIVE,
            size=12,
            visible=False,
            weight="bold",
        )

        self.controls = [self._field, self._error]

    def is_isolated(self) -> bool:
        return True

    def _on_change(self, e: ft.ControlEvent) -> None:
        if self._error.visible and (self._field.value or "").strip():
            self.clear_error()
            self.update()

    @property
    def value(self) -> str:
        return self._field.value

    @value.setter
    def value(self, v: str) -> None:
        self._field.value = v

    def focus(self) -> None:
        self._field.focus()

    def set_error(self, message: str) -> None:
        self._field.border_color = AppColors.INTENT_DESTRUCTIVE
        self._field.focused_border_color = AppColors.INTENT_DESTRUCTIVE
        self._error.value = message
        self._error.visible = True
        self.update()

    def clear_error(self) -> None:
        self._field.border_color = self._normal_border_color
        self._field.focused_border_color = self._normal_focused_border_color
        self._error.value = ""
        self._error.visible = False
