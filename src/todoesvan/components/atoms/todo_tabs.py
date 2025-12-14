from typing import Callable

import flet as ft

from todoesvan.utils.theme import AppColors


class TodoTabs(ft.Tabs):
    def __init__(self, on_change_tab: Callable[[ft.ControlEvent], None]):
        super().__init__()

        self.on_change = on_change_tab

        self.selected_index = 0
        self.animation_duration = 300
        self.indicator_color = AppColors.ACCENT
        self.label_color = AppColors.ACCENT
        self.unselected_label_color = AppColors.TEXT_PRIMARY
        self.divider_color = AppColors.BORDER_DEFAULT

        self.tabs = [
            ft.Tab(text="Active"),
            ft.Tab(text="Completed"),
        ]
