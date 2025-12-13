import flet as ft
from utils.theme import AppColors

class TodoInput(ft.Column):
    def __init__(self, on_submit_action):
        super().__init__()
        self.expand = True
        self.spacing = 4  # space between input and error text

        # Real TextField
        self._field = ft.TextField(
            on_submit=on_submit_action,
            on_change=self._on_change,   # ✅ clear error as soon as input becomes valid
            hint_text="What needs to be done?",
            hint_style=ft.TextStyle(color=AppColors.HINT_TEXT),
            text_style=ft.TextStyle(color=AppColors.TEXT),
            height=50,  # input stays 50px tall
            border_color=AppColors.BORDER,
            focused_border_color=AppColors.ACCENT,
            max_length=50
        )

        # Store normal colors to restore later
        self._normal_border_color = AppColors.BORDER
        self._normal_focused_border_color = AppColors.ACCENT

        # Error text below (outside the TextField)
        self._error = ft.Text(
            value="",
            color=AppColors.DANGER,
            size=12,
            visible=False,
            weight="bold",
        )

        self.controls = [self._field, self._error]

    def _on_change(self, e: ft.ControlEvent):
        # Only clear if an error is currently shown AND the input has a non-space character
        if self._error.visible and (self._field.value or "").strip():
            self.clear_error()

    # --- Proxy API (so HomeView code stays the same) ---
    @property
    def value(self):
        return self._field.value

    @value.setter
    def value(self, v):
        self._field.value = v

    def focus(self):
        self._field.focus()

    def update(self):
        # Ensure Column updates properly
        super().update()

    # --- Error API ---
    def set_error(self, message: str):
        self._field.border_color = AppColors.DANGER
        self._field.focused_border_color = AppColors.DANGER

        self._error.value = message
        self._error.visible = True
        self.update()

    def clear_error(self):
        self._field.border_color = self._normal_border_color
        self._field.focused_border_color = self._normal_focused_border_color

        self._error.value = ""
        self._error.visible = False
        self.update()
