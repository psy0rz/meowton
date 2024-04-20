import peewee
from nicegui import ui

import ui_common
import ui_main
from db_cat import DbCat
from meowton import meowton


@ui.page('/feeder')
def feeder_page():
    ui_common.header("Feeder")


    with ui.card():
        ui.label("Feed settings").classes('text-primary text-bold')

        with ui.label("Speed and direction"):
            ui.slider( min=5, max=8, step=0.1).props("label label-always").bind_value(meowton.feeder,'feed_duty')
        ui.label("(PWM dutycycle range between 5% and 10%)")
        ui.number(label="Feed time").bind_value(meowton.feeder,'feed_time')



        with ui.card_actions():
            ui.button("Test", on_click=meowton.feeder.feed_cycle)
            # ui.button("Calibrate", on_click=lambda: calibrate_wizard(scale, cal_weight))

    ui_common.footer()
