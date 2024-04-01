import asyncio

from nicegui import ui

from scale import Scale
from scale_instances import scale_cat, scale_food, sensor_filter_cat, sensor_filter_food
from sensor_filter import SensorFilter


def calibrate_wizard(scale: Scale, cal_weight: int):
    with ui.dialog(value=True) as dialog:
        with ui.stepper() as stepper:
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


def settings_dialog(scale: Scale, filter: SensorFilter):
    with ui.dialog(value=True) as dialog, ui.card():
        ui.label(f"Options {scale.name} scale")
        filter_diff_input = ui.number("Input filtering", value=filter.filter_diff, precision=0, min=0)

        def save():
            filter.filter_diff = filter_diff_input.value
            dialog.close()

        with ui.row():
            ui.button('Save', on_click=save)
            ui.button('Cancel', on_click=dialog.close).props('flat')


def scale_card(scale: Scale, cal_weight: int, filter: SensorFilter):
    with ui.card():
        ui.markdown(f"**{scale.name} scale**")
        with ui.grid(columns=2):
            ui.label("Last sensor difference:")
            ui.label("...").bind_text_from(filter, 'last_difference', backward=lambda v: f"{v}")

            ui.label("Filtered sensor value:")
            ui.label("...").bind_text_from(scale, 'last_realtime_raw_value', backward=lambda v: f"{v}")

            # ui.label("Last ignored difference:")
            # ui.label("...").bind_text_from(filter, 'last_ignored_diff', backward=lambda v: f"{v}")

            ui.label("Weight: ")
            ui.label("...").bind_text_from(scale, 'last_realtime_weight', backward=lambda v: f"{v:.2f}g")

        with ui.card_actions():
            ui.button(icon='settings', on_click=lambda: settings_dialog(scale, filter))
            ui.button("Tarre", on_click=scale.tarre)
            ui.button("Calibrate", on_click=lambda: calibrate_wizard(scale, cal_weight))


@ui.page('/calibrate')
async def content():
    with ui.header(elevated=True).classes('items-center justify-between'):
        with ui.link(target='/'):
            ui.button(icon='arrow_back').props('flat color=white')
        ui.label('CALIBRATION')

    scale_card(scale_cat, 200, sensor_filter_cat)
    scale_card(scale_food, 10, sensor_filter_food)
