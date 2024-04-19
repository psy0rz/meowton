import settings
import ui_page_calibrate
import ui_page_cats
from cat import Cat
from meowton import meowton
from ui_common import footer

print("Loading nicegui...")
from nicegui import ui, nicegui

print("Loading nicegui done.")


def main_header():
    with ui.header(elevated=True).classes('items-center justify-between'):
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        ui.label("MEOWTON")


with ui.left_drawer(elevated=True, value=False) as left_drawer:
    # with ui.scroll_area().classes("fit"):
    with ui.list().props('separator clickable').classes("fit"):
        with ui.item(on_click=lambda: ui.navigate.to(ui_page_cats.overview_page)):
            with ui.item_section():
                ui.item_label('My cats')
        with ui.item(on_click=lambda: ui.navigate.to(ui_page_calibrate.calibrate_cat_page)):
            with ui.item_section():
                ui.item_label('Cat scale status')
        with ui.item(on_click=lambda: ui.navigate.to(ui_page_calibrate.calibrate_food_page)):
            with ui.item_section():
                ui.item_label('Food scale status')


def main_page():

    with ui.row():
        with (ui.card()):
            ui.label("Scale").classes("text-primary text-bold")
            with ui.row():
                progress = ui.circular_progress(0, min=0, max=meowton.cat_scale.stable_measurements, color="red")
                progress.bind_value_from(meowton.cat_scale, 'measure_countdown').props("instant-feedback")

                label = ui.label()
                label.bind_text_from(meowton.cat_scale, 'last_stable_weight', backward=lambda x: f"{x:.0f}g")
                label.classes("text-bold")

        with (ui.card()):
            ui.label("Food").classes("text-primary text-bold")
            with ui.row():
                progress = ui.circular_progress(0, min=0, max=meowton.food_scale.stable_measurements, color="red")
                progress.bind_value_from(meowton.food_scale, 'measure_countdown').props("instant-feedback")

                label = ui.label()
                label.bind_text_from(meowton.food_scale, 'last_stable_weight', backward=lambda x: f"{x:.1f}g")
                label.classes("text-bold")


    cat_name=ui.label("cat")
    def cat_detected(cat:Cat):
        if cat is None:
            cat_name.set_text("(none)")
        else:

            cat_name.set_text(cat.name)

    meowton.cat_detector.subscribe(cat_detected)


main_header()
main_page()
footer()

# with ui.timeline(side='right'):
#     with ui.timeline_entry(
#             title='Mogwai stole 4g in 30 seconds.',
#             subtitle='4 minutes ago', color='red'):
#         ui.label("Has to wait 130 minutes for more food.")
#         ui.label("Weight: 6.2Kg")
#     with ui.timeline_entry(title='Tracy ate 12g in 1 minute', subtitle='5 minutes ago'):
#         ui.label("Has has 33g left.")
#         ui.label("Weight: 3.2Kg")
#
#     with ui.timeline_entry(
#             title='Mogwai ate 6g in 1 minute.',
#             subtitle='15 minutes ago', color='red'):
#         ui.label("Has to wait 120 minutes for more food.")
#         ui.label("Weight: 6.2Kg")
#     with ui.timeline_entry(
#             title='Mogwai sat on the scale for 3 minutes',
#             subtitle='15 minutes ago', color='red'):
#         ui.label("Has to wait 120 minutes for more food.")
#         ui.label("Weight: 6.2Kg")
#     with ui.timeline_entry(
#             title='Mogwai ate 6g',
#             subtitle='15 minutes ago', color='red'):
#         ui.label("Has to wait 120 minutes for more food.")
#         ui.label("Weight: 6.2Kg")
#
#     with ui.timeline_entry(
#             title='Mogwai ate 8g',
#             subtitle='5 hours ago', color='red'):
#         ui.label("Has to wait 65 minutes for more food.")
#         ui.label("Weight: 6.2Kg")
#
#     ui.timeline_entry()


def run(startup_cb, shutdown_cb):

    nicegui.app.on_startup(startup_cb)
    nicegui.app.on_shutdown(shutdown_cb)
    ui.run(reload=settings.dev_mode, show=False)

