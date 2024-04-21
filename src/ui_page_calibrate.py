from nicegui import ui

import settings
import ui_common
from meowton import meowton
from scale import Scale
from sensor_filter import SensorFilter


def calibrate_wizard(scale: Scale, cal_weight: int):
    with ui.dialog(value=True) as dialog:
        if settings.dev_mode:
            dialog.props("seamless")

        with ui.stepper().props("contracted") as stepper:
            with ui.step(f'Tarre'):
                ui.label(f'Remove all objects from {scale.name} scale. Press next to tarre.')

                def tarre():
                    scale.tarre()
                    scale.calibration.save()
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
                    scale.calibration.save()
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


def sensor_settings_dialog(sensor_filter: SensorFilter):
    with ui.dialog(value=True) as dialog, ui.card():
        ui.label(f"Sensor settings {sensor_filter.name} scale")
        filter_diff_input = ui.number("Filter changes above", value=sensor_filter.filter_diff, precision=0, min=0)

        def save():
            sensor_filter.filter_diff = filter_diff_input.value
            sensor_filter.save()
            dialog.close()

        with ui.row():
            ui.button('Save', on_click=save)
            ui.button('Cancel', on_click=dialog.close).props('flat')


def scale_settings_dialog(scale: Scale):
    with ui.dialog(value=True) as dialog, ui.card():
        ui.label(f"Settings {scale.name} scale")
        stable_range = ui.number("Stable range (g)", value=scale.stable_range, precision=3, min=0.001)
        stable_measurements = ui.number("Stable countdown", value=scale.stable_measurements, precision=0, min=1)

        def save():
            scale.stable_range = stable_range.value
            scale.stable_measurements = stable_measurements.value

            scale.save()
            dialog.close()

        with ui.row():
            ui.button('Save', on_click=save)
            ui.button('Cancel', on_click=dialog.close).props('flat')


def cards(scale: Scale, cal_weight: int):
    def tarre():
        scale.tarre()
        scale.calibration.save()
        ui.notify("tarred")


    with ui.card():
        ui.label("1. Sensor input").classes('text-primary text-bold')
        with ui.grid(columns=2):
            ui.label("Change:")
            ui.label("...").bind_text_from(scale.sensor_filter, 'last_difference', backward=lambda v: f"{v}")

            ui.label("Filtered value:")
            ui.label("...").bind_text_from(scale, 'last_realtime_raw_value', backward=lambda v: f"{v}")

        with ui.card_actions():
            ui.button(icon='settings', on_click=lambda: sensor_settings_dialog(scale.sensor_filter))

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
            ui.button("Tarre", on_click=tarre)
            ui.button("Calibrate", on_click=lambda: calibrate_wizard(scale, cal_weight))

    with ui.card().style("min-width: 20em"):
        ui.label("3. Measuring").classes('text-primary text-bold')

        with ui.row():
            progress = ui.circular_progress(0, min=0, max=scale.stable_measurements, color="red")
            progress.bind_value_from(scale, 'measure_countdown').props("instant-feedback")

            label = ui.label()
            label.bind_text_from(scale, 'last_stable_weight', backward=lambda x: f"{x:0.2f}g")
            label.classes("text-bold")

        ui.separator()

        ui.label("Movement range:")
        ui.linear_progress(0, show_value=False).bind_value_from(scale, 'measure_spread', backward=lambda
            v: scale.measure_spread / scale.stable_range).props("instant-feedback")
        ui.label("...").bind_text_from(scale, 'measure_spread', backward=lambda v: f"{v:.2f}g")
        # ui.circular_progress(0,min=0,max=scale.stable_range, color="green").bind_value_from(scale,'measure_spread').props("instant-feedback")

        with ui.card_actions():
            ui.button(icon='settings', on_click=lambda: scale_settings_dialog(scale))


@ui.page('/cat-scale')
async def calibrate_cat_page():
    ui_common.header("cat scale calibration")
    ui_common.footer()

    cards(meowton.cat_scale, 200)


@ui.page('/food-scale')
async def calibrate_food_page():
    ui_common.header("food scale calibration")
    ui_common.footer()

    cards(meowton.food_scale, 10)
