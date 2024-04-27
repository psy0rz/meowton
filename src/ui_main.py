import settings
import ui_page_calibrate
import ui_page_cats
import ui_page_feeder
import ui_page_schedule
from db_cat import DbCat
from feeder import Status
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
        with ui.item(on_click=lambda: ui.navigate.to(ui_page_schedule.overview_page)):
            with ui.item_section():
                ui.item_label('Feeding schedule')

        ui.item_label('Configuration:').props("header")
        ui.separator()
        with ui.item(on_click=lambda: ui.navigate.to(ui_page_calibrate.calibrate_cat_page)).props("inset-level=1"):
            with ui.item_section():
                ui.item_label('Cat scale')
        with ui.item(on_click=lambda: ui.navigate.to(ui_page_calibrate.calibrate_food_page)).props("inset-level=1"):
            with ui.item_section():
                ui.item_label('Food scale')
        with ui.item(on_click=lambda: ui.navigate.to(ui_page_feeder.feeder_page)).props("inset-level=1"):
            with ui.item_section():
                ui.item_label('Feeder')


@ui.refreshable
def main_page():

    with ui.grid(columns='auto 3em auto').classes(""):
        # scale progress
        progress = ui.circular_progress(0, min=0, max=meowton.cat_scale.stable_measurements, color="purple")
        progress.bind_value_from(meowton.cat_scale, 'measure_countdown').props("instant-feedback")

        label = ui.label()
        label.bind_text_from(meowton.cat_scale, 'last_stable_weight', backward=lambda x: f"{x:.0f}g")
# /        label.classes("text-bold")

        # scale status
        cat_status_ok = ui.label("").bind_text_from(meowton.cat_detector, 'status_msg').classes("text-positive text-bold")
        cat_status_ok.bind_visibility_from(meowton.cat_detector, 'status', backward=lambda v: v == Status.OK)

        cat_status_busy = ui.label("").bind_text_from(meowton.cat_detector, 'status_msg').classes(
            "text-accent text-bold")
        cat_status_busy.bind_visibility_from(meowton.cat_detector, 'status', backward=lambda v: v == Status.BUSY)

        cat_status_error = ui.label("").bind_text_from(meowton.cat_detector, 'status_msg').classes(
            "text-negative text-bold")
        cat_status_error.bind_visibility_from(meowton.cat_detector, 'status', backward=lambda v: v == Status.ERROR)


        # food progress
        progress = ui.circular_progress(0, min=0, max=meowton.food_scale.stable_measurements, color="purple")
        progress.bind_value_from(meowton.food_scale, 'measure_countdown').props("instant-feedback")

        label = ui.label()
        label.bind_text_from(meowton.food_scale, 'last_stable_weight', backward=lambda x: f"{x:.1f}g")
        # label.classes("text-bold")

        # feeder status
        status_ok = ui.label("").bind_text_from(meowton.feeder, 'status_msg').classes("text-positive text-bold")
        status_ok.bind_visibility_from(meowton.feeder, 'status', backward=lambda v: v == Status.OK)

        status_busy = ui.label("").bind_text_from(meowton.feeder, 'status_msg').classes(
            "text-accent text-bold")
        status_busy.bind_visibility_from(meowton.feeder, 'status', backward=lambda v: v == Status.BUSY)

        status_error = ui.label("").bind_text_from(meowton.feeder, 'status_msg').classes(
            "text-negative text-bold")
        status_error.bind_visibility_from(meowton.feeder, 'status', backward=lambda v: v == Status.ERROR)

    # cats overview
    with ui.row():
        for cat in DbCat.cats.values():
            with ui.card() as cat_card:
                with ui.row():
                    ui.label(f"{cat.name}").classes("text-h6")
                    ui.button(icon="bar_chart", on_click=lambda x: print(x)).props("flat ")

                with ui.card_section():
                    ui.label().bind_text_from(cat,'weight', backward=lambda v : f"{v:.0f}g").classes("text-bold text-centered")

                with ui.row():
                    ui.label().bind_text_from(cat, 'feed_quota', backward=lambda v: f"{v:.1f}g")
                    ui.label(f"(of {cat.feed_daily:.0f}g)")

    ui.button("feed", on_click=meowton.feeder.request)
    ui.button("forced feed", on_click=meowton.feeder.forward)


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
