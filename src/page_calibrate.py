import asyncio

from nicegui import ui

from scale import Scale
from scale_instances import scale_cat, scale_food


def calibrate_wizard(scale: Scale, cal_weight:int):
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
                cal_weight = ui.input(label='Calibration weight (g)', value=cal_weight)

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


def scale_card(scale:Scale, cal_weight:int):

    with ui.card():
        ui.markdown(f"**{scale.name} scale**")
        with ui.grid(columns=2):
            ui.label("Raw value:")
            ui.label("...").bind_text_from(scale, 'last_realtime_raw_value', backward=lambda v: f"{v}")

            ui.label("Weight: ")
            ui.label("...").bind_text_from(scale, 'last_realtime_weight', backward=lambda v: f"{v}g")

        with ui.card_actions():
            ui.button("Tarre", on_click=scale.tarre)
            ui.button("Calibrate", on_click=lambda: calibrate_wizard(scale, cal_weight))

@ui.page('/calibrate')
async def content():
    with ui.header(elevated=True).classes('items-center justify-between'):
        with ui.link(target='/'):
            ui.button(icon='arrow_back').props('flat color=white')
        ui.label('CALIBRATION')

    scale_card(scale_cat, 200)
    scale_card(scale_food, 10)


