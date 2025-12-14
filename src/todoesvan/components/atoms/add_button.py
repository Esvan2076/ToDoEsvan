from typing import Callable

import flet as ft

from todoesvan.utils.theme import AppColors, UISizes


class AddButton(ft.Container):
    def __init__(self, on_click_action: Callable[[ft.ControlEvent], None]):
        super().__init__()

        self.height = UISizes.ICON_BUTTON
        self.width = UISizes.ICON_BUTTON

        self.content = ft.ElevatedButton(
            on_click=on_click_action,
            content=ft.Icon(ft.Icons.ADD),
            width=UISizes.ICON_BUTTON,
            height=UISizes.ICON_BUTTON,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),

                bgcolor={
                    ft.ControlState.DEFAULT: AppColors.ACCENT,
                    ft.ControlState.PRESSED: AppColors.BG_PRIMARY,
                },

                side={
                    ft.ControlState.DEFAULT: ft.BorderSide(0, "transparent"),
                    ft.ControlState.PRESSED: ft.BorderSide(2, AppColors.ACCENT),
                },

                color={
                    ft.ControlState.DEFAULT: "black",
                    ft.ControlState.PRESSED: AppColors.ACCENT,
                },

                elevation={
                    ft.ControlState.DEFAULT: 0,
                    ft.ControlState.PRESSED: 0,
                },
            ),
        )
