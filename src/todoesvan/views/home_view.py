import flet as ft

from todoesvan.components.atoms.add_button import AddButton
from todoesvan.components.atoms.todo_input import TodoInput
from todoesvan.components.atoms.todo_tabs import TodoTabs
from todoesvan.components.organisms.todo_list import TodoList
from todoesvan.data.repositories.task_repository import TaskRepository
from todoesvan.services.task_service import TaskService
from todoesvan.state.task_store import TaskStore
from todoesvan.utils.theme import AppColors


class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/", padding=20, bgcolor=AppColors.BG_PRIMARY)
        self.page = page

        # Data
        repo = TaskRepository()
        service = TaskService(repo)

        # UI
        self.input_atom = TodoInput(on_submit_action=self.trigger_add)
        self.tabs_atom = TodoTabs(on_change_tab=self.handle_tab_change)
        self.button_atom = AddButton(on_click_action=self.trigger_add)

        self.todo_list_atom = TodoList(
            on_delete_task=self.delete_task,
            on_status_change=self.change_status,
            on_update_subject=self.update_subject,
        )

        # Store (cache + refresh + optimistic)
        self.store = TaskStore(
            service=service,
            schedule=self.page.run_task,
            on_change=self._render_active,
            on_error=self._snack,
        )

        self.controls = [
            ft.Text("My To-Do List", size=30, weight="bold", color=AppColors.TEXT_PRIMARY),
            ft.Row([self.input_atom, self.button_atom], vertical_alignment=ft.CrossAxisAlignment.START),
            self.tabs_atom,
            self.todo_list_atom,
        ]

    def did_mount(self):
        self._render_active()
        self.store.warm_cache_both()

    # -------------------------
    # UI helpers
    # -------------------------
    def _snack(self, msg: str) -> None:
        self.page.snack_bar = ft.SnackBar(content=ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

    def _is_completed_tab(self) -> bool:
        return self.tabs_atom.selected_index == 1

    def _render_active(self) -> None:
        key = self._is_completed_tab()
        self.todo_list_atom.render_tasks(
            self.store.tasks(key),
            pending_ids=self.store.pending_ids,
            refreshing=self.store.is_refreshing(key),
        )

    # -------------------------
    # Events
    # -------------------------
    def handle_tab_change(self, e: ft.ControlEvent) -> None:
        self._render_active()
        self.store.refresh_tab(self._is_completed_tab())

    def trigger_add(self, e: ft.ControlEvent) -> None:
        title = (self.input_atom.value or "").strip()

        if not title:
            self.input_atom.set_error("Task cannot be empty.")
            self.input_atom.focus()
            self.update()
            return

        self.input_atom.clear_error()
        self.input_atom.value = ""
        self.input_atom.focus()
        self.update()

        self.store.create_task(title)

    def delete_task(self, task_id: int) -> None:
        self.store.delete_task(task_id)

    def change_status(self, task_id: int, completed: bool) -> None:
        self.store.toggle_completed(task_id, completed)

    def update_subject(self, task_id: int, subject: str) -> None:
        self.store.update_subject(task_id, subject)
