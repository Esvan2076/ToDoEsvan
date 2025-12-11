import flet as ft
from views.home_view import HomeView

def main(page: ft.Page):
    # Window configuration
    page.title = "ToDo App"
    page.window.icon="assets/icon.png"
    page.window.height = 900
    page.window.width= 450
    page.padding = 20
    
    # Load the main interface
    app_view = HomeView(page)
    
    # Add the view to the screen
    page.add(app_view)

ft.app(main)