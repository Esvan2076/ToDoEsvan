import flet as ft

from components.atoms.add_button import AddButton
from components.atoms.todo_input import TodoInput
from components.atoms.todo_tabs import TodoTabs
from components.organisms.todo_list import TodoList
from data import crud
from utils.theme import AppColors

def HomeView(page: ft.Page):
    page.bgcolor = AppColors.BACKGROUND

    # --- LÓGICA DE ACTUALIZACIÓN ---
    
    def refresh_list():
        # Cuando una tarea cambia de estado, recargamos todo
        load_data()

    def delete_task_wrapper(task_item):
        # El TodoList nos pasa el item, nosotros lo borramos de la BD
        crud.delete_task(task_item.task.id)
        # Y le decimos al TodoList que se actualice (podemos recargar todo o borrar solo ese)
        # Para evitar race conditions visuales, recargamos los datos:
        load_data()

    # --- COMPONENTE LISTA (Instancia) ---
    todo_list_atom = TodoList(
        on_delete_task=delete_task_wrapper,
        on_status_change=refresh_list
    )

    # --- FUNCIÓN MAESTRA DE CARGA ---
    def load_data():
        # 1. ¿Qué pestaña quiere el usuario?
        is_completed_tab = (tabs_atom.selected_index == 1)
        
        # 2. Inmediatamente ponemos la UI en modo "Cargando" (Gris)
        todo_list_atom.show_loading()
        
        # 3. Vamos a la BD (Esto puede tardar milisegundos)
        # Flet bloqueará un poco aquí, pero como ya pintamos el gris, se siente fluido
        db_tasks = crud.get_tasks(completed_status=is_completed_tab)
        
        # 4. Le entregamos los datos a la lista para que ella decida qué pintar
        todo_list_atom.render_tasks(db_tasks)

    # --- MANEJADORES DE EVENTOS ---

    def handle_tab_change(e):
        # Al cambiar de tab, ejecutamos la carga maestra
        load_data()

    # 3. Add Task Logic
    def trigger_add(e):
        raw = input_atom.value or ""
        task_title = raw.strip()

        # ✅ Validación SOLO cuando intentas agregar (click o Enter)
        if not task_title:
            input_atom.set_error("Task cannot be empty.")
            input_atom.focus()
            return

        # ✅ Limpia error si ya es válido
        input_atom.clear_error()

        # ✅ Mandamos a BD ya sanitizado
        crud.create_task(task_title)

        input_atom.value = ""
        input_atom.update()

        # Si agregas, recargas
        load_data()

        # Importante: Mantener el foco
        input_atom.focus()

    # --- INSTANCIAS DE ATOMOS ---
    input_atom = TodoInput(on_submit_action=trigger_add)
    tabs_atom = TodoTabs(on_change_tab=handle_tab_change)
    button_atom = AddButton(on_click_action=trigger_add)

    # Carga Inicial
    load_data()

    # --- LAYOUT FINAL ---
    return ft.Column(
        controls=[
            ft.Text("My To-Do List", size=30, weight="bold", color=AppColors.TEXT),
            
            ft.Row(
                [input_atom, button_atom],
                vertical_alignment=ft.CrossAxisAlignment.START
            ),

            tabs_atom,
            
            # Aquí va nuestro nuevo componente superpoderoso
            todo_list_atom 
        ]
    )