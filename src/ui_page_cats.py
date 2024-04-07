from nicegui import ui

import ui_main
from cat import Cat



@ui.refreshable
def cat_list():
    def delete_button(cat: Cat):
        def confirmed():
            print("JAHOOOR")
            cat.delete_instance()
            cat_list.refresh()


        def delete():
            ui_main.confirm(message=f"Delete cat {cat.name} {cat.id}?", on_confirm=confirmed)
        ui.button(icon="delete", on_click=delete)


    for cat in Cat.select():
        with ui.card():
            ui.label(cat.name).classes("text-primary text-bold")

            with ui.grid(columns=2):
                ui.label("Weight:")
                ui.label(cat.weight)

                ui.label("Daily quota:")
                ui.label(cat.feed_daily)

            with ui.card_actions():
                ui.button(icon="settings")

                delete_button(cat)


@ui.page('/cats')
def overview_page():
    ui_main.header("Cats")
    cat_list()
    ui_main.footer()


