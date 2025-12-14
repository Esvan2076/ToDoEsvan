from flet import Page

from todoesvan.utils.assets import asset_path
from todoesvan.views.home_view import HomeView


class MainView:
    def __init__(self, page: Page) -> None:
        self.page: Page = page
        self._configure_page()
        self._build()

    def _configure_page(self) -> None:
        """Apply initial page config like title, size, icon"""
        self.page.title = "ToDo Esvan"
        self.page.window.height = 900
        self.page.window.width = 450
        self.page.window.icon = asset_path("icon.ico")
        self.page.padding = 20

    def _build(self) -> None:
        """Add the initial view to the page"""
        self.page.views.clear()
        self.page.views.append(HomeView(self.page))
        self.page.update()


def main(page: Page) -> None:
    """Main entry point expected by flet.app"""
    MainView(page)
