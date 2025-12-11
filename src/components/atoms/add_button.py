import flet as ft
from utils.theme import AppColors

class AddButton(ft.Container):
    def __init__(self, on_click_action):
        super().__init__()
        self.on_click_action = on_click_action
        
        # Configuramos el contenedor
        self.height = 50
        self.width = 50
        self.content = ft.ElevatedButton(
            on_click=self.on_click_action,
            content=ft.Icon(ft.Icons.ADD),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                
                # Background: Default vs Pressed
                bgcolor={
                    "": AppColors.ACCENT,
                    "pressed": AppColors.BACKGROUND
                },
                
                # Border: Default vs Pressed
                side={
                    "": ft.BorderSide(0, "transparent"),
                    "pressed": ft.BorderSide(2, AppColors.ACCENT)
                },
                
                # Icon Color: Default vs Pressed
                color={
                    "": "black",
                    "pressed": AppColors.ACCENT
                },
                
                elevation={"pressed": 0, "": 0},
            ),
            width=50,
            height=50
        )