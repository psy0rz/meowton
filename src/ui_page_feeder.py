import peewee
from nicegui import ui

import feeder
import ui_common
import ui_main
from db_cat import DbCat
from meowton import meowton


@ui.page('/feeder')
def feeder_page():
    ui_common.header("Feeder")

    with ui.row():
        with ui.card():
            ui.label("Feed amount").classes('text-primary text-bold')

            ui.label("Speed and direction:")
            feed_duty = ui.slider(min=feeder.SERVO_MIN, max=feeder.SERVO_MAX, step=0.1,
                                  value=meowton.feeder.feed_duty).props("label")

            feed_time = ui.number(label="Feed time (mS)", value=meowton.feeder.feed_time)

            with ui.card_actions():
                ui.button("Test", on_click=lambda: meowton.feeder.run_motor(feed_duty.value, feed_time.value))

        with ui.card():
            ui.label("Reverse jammer").classes('text-primary text-bold')

            ui.label("Speed and direction:")
            reverse_duty = ui.slider(min=feeder.SERVO_MIN, max=feeder.SERVO_MAX, step=0.1,
                                     value=meowton.feeder.reverse_duty).props("label")

            reverse_time = ui.number(label="Reverse time (mS)", value=meowton.feeder.reverse_time)

            with ui.card_actions():
                ui.button("Test", on_click=lambda: meowton.feeder.run_motor(reverse_duty.value, reverse_time.value))

    def save():
        meowton.feeder.feed_duty = feed_duty.value
        meowton.feeder.feed_time = feed_time.value
        meowton.feeder.reverse_duty = reverse_duty.value
        meowton.feeder.reverse_time = reverse_time.value
        meowton.feeder.save()
        ui.notify("saved")
        ui.navigate.back()

    ui.button(icon="save", on_click=save)
    ui_common.footer()
