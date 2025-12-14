import flet as ft

from todoesvan.components.atoms.add_button import AddButton
from todoesvan.components.atoms.todo_input import TodoInput
from todoesvan.components.atoms.todo_tabs import TodoTabs
from todoesvan.components.organisms.todo_list import TodoList
from todoesvan.data.repositories.task_repository import TaskRepository
from todoesvan.services.task_service import TaskService
from todoesvan.utils.theme import AppColors


class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/",
            padding=20,
            bgcolor=AppColors.BG_PRIMARY,
        )

        self.page: ft.Page = page

        # Data layer (Repo -> Service)
        self.repo: TaskRepository = TaskRepository()
        self.service: TaskService = TaskService(self.repo)

        # UI atoms/organisms
        self.input_atom: TodoInput = TodoInput(on_submit_action=self.trigger_add)
        self.tabs_atom: TodoTabs = TodoTabs(on_change_tab=self.handle_tab_change)
        self.button_atom: AddButton = AddButton(on_click_action=self.trigger_add)

        # TodoList with task ID based callbacks
        self.todo_list_atom: TodoList = TodoList(
            on_delete_task=self.delete_task,
            on_status_change=self.change_status,
        )

        # Layout
        self.controls: list[ft.Control] = [
            ft.Text("My To-Do List", size=30, weight="bold", color=AppColors.TEXT_PRIMARY),
            ft.Row(
                [self.input_atom, self.button_atom],
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            self.tabs_atom,
            self.todo_list_atom,
        ]

        self.load_data()

    # -------------------------
    # Event handlers
    # -------------------------

    def handle_tab_change(self, e: ft.ControlEvent) -> None:
        """Triggered when user switches tabs"""
        self.load_data()

    def trigger_add(self, e: ft.ControlEvent) -> None:
        """Triggered when user submits a new task"""
        raw = self.input_atom.value or ""
        title = raw.strip()

        if not title:
            self.input_atom.set_error("Task cannot be empty.")
            self.input_atom.focus()
            self.update()
            return

        self.input_atom.clear_error()
        self.service.add_task(title)
        self.input_atom.value = ""
        self.load_data()
        self.input_atom.focus()
        self.update()

    def delete_task(self, task_id: int) -> None:
        """Triggered when a task is deleted"""
        self.service.delete_task(task_id)
        self.load_data()

    def change_status(self, task_id: int, completed: bool) -> None:
        """Triggered when a task is toggled (completed/uncompleted)"""
        self.service.toggle_completed(task_id, completed)
        self.load_data()

    # -------------------------
    # Internal logic
    # -------------------------

    def _is_completed_tab(self) -> bool:
        """Returns True if the current tab is 'Completed'"""
        return self.tabs_atom.selected_index == 1

    def load_data(self) -> None:
        """Refreshes the task list from service"""
        self.todo_list_atom.show_loading()
        tasks = self.service.get_tasks(completed=self._is_completed_tab())
        self.todo_list_atom.render_tasks(tasks)
