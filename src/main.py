import flet as ft
from views.home_view import HomeView

def main(page: ft.Page):
    # Window configuration
    page.title = "ToDo Esvan"
    page.window.height = 900
    page.window.width= 450
    page.window.icon = "icon.ico"
    page.padding = 20
    page.update()
    
    # Load the main interface
    app = HomeView(page)
    
    # Add the view to the screen
    page.add(app)

ft.app(target=main, assets_dir="assets")