from nicegui import ui


@ui.page('/calibrate')
def content():
    print("AANGEROEPE")
    with ui.header(elevated=True).classes('items-center justify-between'):
        with ui.link(target='/'):
            ui.button(icon='arrow_back').props('flat color=white')
        ui.label('CALIBRATION')


    ui.label("hoi")


    weight_label = ui.label('...')

    def ding():
        print("boxe")
        weight_label.set_text(str(time.time()))
    ui.timer(1, ding)

    # scale.subscribe_realtime(lambda weight: weight_label.set_text(f"{weight}g {weight_label.client.on_air}"))

    # weight_label.client.on_disconnect(lambda: print ("DE KEUTEL"))
