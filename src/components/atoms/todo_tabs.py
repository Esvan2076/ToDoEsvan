import flet as ft
from utils.theme import AppColors

class TodoTabs(ft.Tabs):
    def __init__(self, on_change_tab):
        super().__init__()
        
        # Guardamos la función que nos pasa el Padre para llamarla luego
        self.on_change = on_change_tab
        
        # Configuración visual (El estilo que te gustó)
        self.selected_index = 0  # Empieza en la primera pestaña
        self.animation_duration = 300
        self.indicator_color = AppColors.ACCENT
        self.label_color = AppColors.ACCENT
        self.unselected_label_color = AppColors.TEXT
        self.divider_color = AppColors.BORDER
        
        # Definimos las pestañas
        self.tabs = [
            ft.Tab(text="Active"),
            ft.Tab(text="Completed"),
        ]