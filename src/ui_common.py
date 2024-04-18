from nicegui import ui

import settings
from meowton import meowton


def header(title: str):
    with ui.header(elevated=True).classes('items-center justify-between'):
        with ui.link(target='/'):
            ui.button(icon='arrow_back').props('flat color=white')
        ui.label(title.upper())


def footer():
    sim_food_value = 198000
    sim_food_min = 188000
    sim_food_max = 300000

    sim_cat_value = -40000
    sim_cat_min = -50000
    sim_cat_max = 14000

    if settings.dev_mode:
        with ui.footer():
            ui.slider(min=sim_cat_min, max=sim_cat_max, value=sim_food_value).props(
                'flat color=white dense').bind_value(meowton.cat_reader, 'sim_value')
            ui.slider(min=sim_food_min, max=sim_food_max, value=sim_cat_value).props(
                'flat color=white dense').bind_value(meowton.food_reader, 'sim_value')


def confirm(message, on_confirm, title="Confirm"):
    def yes():
        on_confirm()
        popup_dialog.close()

    with ui.dialog(value=True) as popup_dialog, ui.card():
        popup_dialog.on('hide', popup_dialog.delete)

        ui.label(title).classes("text-negative text-bold")
        ui.label(message)

        with ui.card_actions():
            ui.button("Yes", on_click=yes)
            ui.button("No", on_click=popup_dialog.delete)
