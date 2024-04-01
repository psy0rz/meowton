import asyncio
import threading
import time
from pprint import pprint
from random import random

from nicegui.run import cpu_bound

import page_calibrate
import scale_instances
import scale_reader

# from meowton import Meowton
# meowton_instance=Meowton()
# meowton_instance.run()

print("Loading nicegui...")
from nicegui import ui, nicegui

print("Starting...")


@ui.page('/cats')
def cats_page():
    with ui.header(elevated=True).classes('items-center justify-between'):
        with ui.link(target='/'):
            ui.button(icon='arrow_back').props('flat color=white')
        ui.label('CATS')

    ui.label("hoi")


with ui.header(elevated=True).classes('items-center justify-between'):
    ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
    ui.label('HEADER')

with ui.left_drawer(elevated=True, value=False) as left_drawer:
    # with ui.scroll_area().classes("fit"):
        with ui.list().props('separator clickable').classes("fit"):
            with ui.item(on_click=lambda: ui.navigate.to(page_calibrate.calibrate_cat_page)):
                with ui.item_section():
                    ui.item_label('Cat scale status')
            with ui.item(on_click=lambda: ui.notify('Selected contact 1')):
                with ui.item_section():
                    ui.item_label('Nice Guy')
            with ui.item(on_click=lambda: ui.notify('Selected contact 1')):
                with ui.item_section():
                    ui.item_label('Nice Guy')

    # ui.link("Cats", cats_page)
    # ui.link("Cat scale status", page_calibrate.calibrate_cat_page)
# with ui.right_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as right_drawer:
#     ui.label('RIGHT DRAWER')
with ui.footer():
    ui.label('FOOTER')

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


def startup():
    scale_reader.start(scale_instances.scale_cat, scale_instances.scale_food, scale_instances.sensor_filter_cat,
                       scale_instances.sensor_filter_food)


def shutdown():
    scale_reader.stop()

#start nicegui
nicegui.app.on_startup(startup)
nicegui.app.on_shutdown(shutdown)
ui.run(reload=False, show=False)
