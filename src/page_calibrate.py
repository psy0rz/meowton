import asyncio

from nicegui import ui

from scale import Scale
from scale_instances import scale_cat, scale_food, sensor_filter_cat, sensor_filter_food
from sensor_filter import SensorFilter


def calibrate_wizard(scale: Scale, cal_weight: int):
    with ui.dialog(value=True) as dialog:
        with ui.stepper().props("contracted") as stepper:
            with ui.step(f'Tarre'):
                ui.label(f'Remove all objects from {scale.name} scale. Press next to tarre.')

                def tarre():
                    scale.tarre()
                    stepper.next()
                    ui.notify(f"{scale.name} tarred")

                with ui.stepper_navigation():
                    ui.button('Next', on_click=tarre)
                    ui.button('Close', on_click=dialog.close).props('flat')

            with ui.step('Calibrate'):
                ui.label(f'Place calibration weight on {scale.name} scale. Press next to calibrate.')
                cal_weight = ui.number(label='Calibration weight (g)', value=cal_weight, precision=0, min=0)

                def calibrate():
                    scale.calibrate(int(cal_weight.value))
                    ui.notify(f"{scale.name} calibrated with {cal_weight.value}g")
                    stepper.next()

                with ui.stepper_navigation():
                    ui.button('Next', on_click=calibrate)
                    ui.button('Back', on_click=stepper.previous).props('flat')
                    ui.button('Close', on_click=dialog.close).props('flat')

            with ui.step('Done'):
                ui.label(f'{scale.name} scale is now calibrated.')
                with ui.stepper_navigation():
                    ui.button('Close', on_click=dialog.close)
                    ui.button('Back', on_click=stepper.previous).props('flat')


def sensor_settings_dialog(scale: Scale, filter: SensorFilter):
    with ui.dialog(value=True) as dialog, ui.card():
        ui.label(f"Options {scale.name} scale")
        filter_diff_input = ui.number("Filter changes above", value=filter.filter_diff, precision=0, min=0)

        def save():
            filter.filter_diff = filter_diff_input.value
            dialog.close()

        with ui.row():
            ui.button('Save', on_click=save)
            ui.button('Cancel', on_click=dialog.close).props('flat')


def scale_card(scale: Scale, cal_weight: int, filter: SensorFilter):
    with ui.card():
        ui.label("1. Sensor input").classes('text-primary text-bold')
        with ui.grid(columns=2):
            ui.label("Change:")
            ui.label("...").bind_text_from(filter, 'last_difference', backward=lambda v: f"{v}")

            ui.label("Filtered value:")
            ui.label("...").bind_text_from(scale, 'last_realtime_raw_value', backward=lambda v: f"{v}")


        with ui.card_actions():
            ui.button(icon='settings', on_click=lambda: sensor_settings_dialog(scale, filter))


    with ui.card():
        ui.label("2. Calibration").classes('text-primary text-bold')
        with ui.grid(columns=2):

            ui.label("Tarre: ")
            ui.label("...").bind_text_from(scale.calibration, 'offset', backward=lambda v: f"{v:}")

            ui.label("Cal. factor: ")
            ui.label("...").bind_text_from(scale.calibration, 'factor', backward=lambda v: f"{v:.5f}")

            ui.label("Weight: ")
            ui.label("...").bind_text_from(scale, 'last_realtime_weight', backward=lambda v: f"{v:.2f}g")

        with ui.card_actions():
            ui.button("Tarre", on_click=scale.tarre)
            ui.button("Calibrate", on_click=lambda: calibrate_wizard(scale, cal_weight))


@ui.page('/cat-scale')
async def calibrate_cat_page():
    with ui.header(elevated=True).classes('items-center justify-between'):
        with ui.link(target='/'):
            ui.button(icon='arrow_back').props('flat color=white')
        ui.label('CALIBRATION CAT SCALE')

    scale_card(scale_cat, 200, sensor_filter_cat)

@ui.page('/food-scale')
async def calibrate_food_page():
    with ui.header(elevated=True).classes('items-center justify-between'):
        with ui.link(target='/'):
            ui.button(icon='arrow_back').props('flat color=white')
        ui.label('CALIBRATION CAT SCALE')

    scale_card(scale_food, 10, sensor_filter_food)
