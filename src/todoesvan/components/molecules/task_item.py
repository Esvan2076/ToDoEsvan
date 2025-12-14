from typing import Callable, Optional

import flet as ft

from todoesvan.data.model import Task
from todoesvan.utils.theme import AppColors


class TaskItem(ft.Row):
    BTN_SIZE = 40
    ICON_SIZE = 18

    def __init__(
        self,
        task: Task,
        pending: bool,
        on_delete: Callable[[int], None],
        on_toggle: Callable[[int, bool], None],
        on_update_subject: Optional[Callable[[int, str], None]] = None,
    ):
        super().__init__()
        self.task = task
        self.pending = pending
        self.on_delete = on_delete
        self.on_toggle = on_toggle
        self.on_update_subject = on_update_subject

        self._editing = False
        self._original_subject = task.subject

        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

        # --- Checkbox ---
        self.checkbox = ft.Checkbox(
            value=self.task.completed,
            on_change=self._status_changed,
            active_color=AppColors.INTENT_POSITIVE,
            disabled=self.pending,
        )

        # --- Textos ---
        self.title_text = ft.Text(
            value=self.task.subject,
            size=16,
            color=AppColors.TEXT_PRIMARY,
            max_lines=3,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.title_input = ft.TextField(
            value=self.task.subject,
            dense=True,
            max_length=50,
            border=ft.InputBorder.NONE,
            border_width=0,
            bgcolor="transparent",
            text_style=ft.TextStyle(color=AppColors.TEXT_PRIMARY, size=16),
            on_submit=self._commit_edit, # Enter guarda
            on_blur=self._commit_edit,   # Click fuera guarda también
            on_change=self._edit_changed,
        )

        # Contenedor intercambiable
        self.title_container = ft.Container(
            content=self.title_text,
            expand=True
        )

        self.left = ft.Row(
            controls=[self.checkbox, self.title_container],
            spacing=10,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # --- Botones ---
        self.edit_btn = ft.IconButton(
            icon=ft.Icons.EDIT,
            icon_color=AppColors.EDIT,
            icon_size=self.ICON_SIZE,
            width=self.BTN_SIZE,
            on_click=self._start_edit,
            disabled=self.pending or (self.on_update_subject is None),
        )

        self.delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color=AppColors.INTENT_DESTRUCTIVE,
            icon_size=self.ICON_SIZE,
            width=self.BTN_SIZE,
            on_click=self._delete_clicked,
            disabled=self.pending,
        )

        self.save_btn = ft.IconButton(
            icon=ft.Icons.CHECK,
            icon_color=AppColors.INTENT_POSITIVE,
            icon_size=self.ICON_SIZE,
            width=self.BTN_SIZE,
            on_click=self._commit_edit,
            disabled=self.pending,
        )

        # Slots para mantener espacio
        self.empty_slot = ft.Container(width=self.BTN_SIZE, height=self.BTN_SIZE)
        self.spinner_slot = ft.Container(
            width=self.BTN_SIZE,
            height=self.BTN_SIZE,
            alignment=ft.alignment.center,
            content=ft.ProgressRing(width=16, height=16, stroke_width=2),
        )

        self.right = ft.Row(spacing=0)
        self.controls = [self.left, self.right]

        self._sync_ui()

    def is_isolated(self) -> bool:
        return True

    def _sync_ui(self):
        if self.pending:
            self._editing = False
            self.title_container.content = self.title_text
            self.right.controls = [self.empty_slot, self.spinner_slot]
            self.checkbox.disabled = True
            return

        if self._editing:
            self.title_container.content = self.title_input
            # SOLO mostramos el botón de guardar
            self.right.controls = [self.save_btn]
            self.checkbox.disabled = True
        else:
            self.title_container.content = self.title_text
            self.right.controls = [self.edit_btn, self.delete_btn]
            self.checkbox.disabled = False

    def _start_edit(self, e: ft.ControlEvent):
        if self.pending or self.on_update_subject is None:
            return
        self._editing = True
        self._original_subject = self.task.subject
        self.title_input.value = self.task.subject
        self.title_input.error_text = None
        self._sync_ui()
        self.title_container.update() # Importante updatear container al cambiar contenido
        self.update()
        self.title_input.focus()

    def _exit_edit_mode_ui(self):
        """Helper para salir del modo edición visualmente"""
        self._editing = False
        self.title_input.error_text = None
        self._sync_ui()
        self.title_container.update()
        self.update()

    def _edit_changed(self, e: ft.ControlEvent):
        if self.title_input.error_text and (self.title_input.value or "").strip():
            self.title_input.error_text = None
            self.update()

    def _commit_edit(self, e: ft.ControlEvent):
        """Intenta guardar. Si no hay cambios, solo cierra."""
        if not self._editing:
            return

        raw = self.title_input.value or ""
        cleaned = raw.strip()

        if not cleaned:
            self.title_input.error_text = "Task cannot be empty"
            self.update()
            self.title_input.focus()
            return

        # Si es igual al original, solo cerramos sin llamar a la DB
        if cleaned == self._original_subject:
            self.title_text.value = self._original_subject # Aseguramos consistencia
            self._exit_edit_mode_ui()
            return

        # --- Flujo de Guardado ---
        # 1. Actualizamos visualmente el TEXTO
        self.title_text.value = cleaned

        # 2. Cerramos la UI de edición
        self._exit_edit_mode_ui()

        # 3. Llamamos al Store (la Task original sigue intacta hasta que el Store decida)
        if self.on_update_subject:
            self.on_update_subject(self.task.id, cleaned)

    def _status_changed(self, e):
        if self.on_toggle and not self.pending and not self._editing:
            self.on_toggle(self.task.id, self.checkbox.value)

    def _delete_clicked(self, e):
        if self.on_delete and not self.pending and not self._editing:
            self.on_delete(self.task.id)
