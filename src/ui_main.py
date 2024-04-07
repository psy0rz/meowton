import scale_reader
import settings
import ui_page_calibrate
import ui_page_cats

print("Loading nicegui...")
from nicegui import ui, nicegui

print("Loading nicegui done.")


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


def main_header():
    with ui.header(elevated=True).classes('items-center justify-between'):
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        ui.label("MEOWTON")


def header(title: str):
    with ui.header(elevated=True).classes('items-center justify-between'):
        with ui.link(target='/'):
            ui.button(icon='arrow_back').props('flat color=white')
        ui.label(title.upper())


with ui.left_drawer(elevated=True, value=False) as left_drawer:
    # with ui.scroll_area().classes("fit"):
    with ui.list().props('separator clickable').classes("fit"):
        with ui.item(on_click=lambda: ui.navigate.to(ui_page_cats.overview_page)):
            with ui.item_section():
                ui.item_label('Cat scale status')
        with ui.item(on_click=lambda: ui.navigate.to(ui_page_calibrate.calibrate_cat_page)):
            with ui.item_section():
                ui.item_label('Cat scale status')
        with ui.item(on_click=lambda: ui.navigate.to(ui_page_calibrate.calibrate_food_page)):
            with ui.item_section():
                ui.item_label('Food scale status')


# ui.link("Cats", cats_page)
# ui.link("Cat scale status", page_calibrate.calibrate_cat_page)
# with ui.right_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as right_drawer:
#     ui.label('RIGHT DRAWER')
def footer():
    if settings.dev_mode:
        with ui.footer():
            ui.slider(min=scale_reader.sim_cat_min, max=scale_reader.sim_cat_max).props(
                'flat color=white dense').bind_value(scale_reader, 'sim_cat_value')
            ui.slider(min=scale_reader.sim_food_min, max=scale_reader.sim_food_max).props(
                'flat color=white dense').bind_value(scale_reader, 'sim_food_value')


main_header()
footer()

with ui.timeline(side='right'):
    with ui.timeline_entry(
            title='Mogwai stole 4g in 30 seconds.',
            subtitle='4 minutes ago', color='red'):
        ui.label("Has to wait 130 minutes for more food.")
        ui.label("Weight: 6.2Kg")
    with ui.timeline_entry(title='Tracy ate 12g in 1 minute', subtitle='5 minutes ago'):
        ui.label("Has has 33g left.")
        ui.label("Weight: 3.2Kg")

    with ui.timeline_entry(
            title='Mogwai ate 6g in 1 minute.',
            subtitle='15 minutes ago', color='red'):
        ui.label("Has to wait 120 minutes for more food.")
        ui.label("Weight: 6.2Kg")
    with ui.timeline_entry(
            title='Mogwai sat on the scale for 3 minutes',
            subtitle='15 minutes ago', color='red'):
        ui.label("Has to wait 120 minutes for more food.")
        ui.label("Weight: 6.2Kg")
    with ui.timeline_entry(
            title='Mogwai ate 6g',
            subtitle='15 minutes ago', color='red'):
        ui.label("Has to wait 120 minutes for more food.")
        ui.label("Weight: 6.2Kg")

    with ui.timeline_entry(
            title='Mogwai ate 8g',
            subtitle='5 hours ago', color='red'):
        ui.label("Has to wait 65 minutes for more food.")
        ui.label("Weight: 6.2Kg")

    ui.timeline_entry()


def run(startup_cb, shutdown_cb):
    nicegui.app.on_startup(startup_cb)
    nicegui.app.on_shutdown(shutdown_cb)
    ui.run(reload=settings.dev_mode, show=False)
