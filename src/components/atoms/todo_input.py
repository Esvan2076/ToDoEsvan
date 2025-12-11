import flet as ft
from utils.theme import AppColors

class TodoInput(ft.TextField):
    def __init__(self, on_submit_action):
        super().__init__()
        # Event
        self.on_submit = on_submit_action 
        
        self.hint_text = "What needs to be done?"
        self.hint_style = ft.TextStyle(color=AppColors.HINT_TEXT)
        self.text_style = ft.TextStyle(color=AppColors.TEXT)
        self.expand = True
        self.height = 50
        self.border_color = AppColors.BORDER
        self.focused_border_color = AppColors.ACCENT