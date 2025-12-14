import flet as ft

from todoesvan.utils.assets import ASSETS_DIR
from todoesvan.views.app_view import main


def run_app() -> None:
    ft.app(
        target=main,
        assets_dir=str(ASSETS_DIR),
    )

if __name__ == "__main__":
    run_app()
