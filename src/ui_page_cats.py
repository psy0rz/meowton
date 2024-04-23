import peewee
from nicegui import ui

import ui_common
import ui_main
from db_cat import DbCat


def delete_button(cat: DbCat):
    def confirmed():
        cat.delete_instance()
        cat_list.refresh()

    def click():
        ui_common.confirm(message=f"Delete cat {cat.name} ?", on_confirm=confirmed)

    ui.button(icon="delete", on_click=click).props("color=red")


def cat_card(cat: DbCat):
    def save():
        try:
            cat.save()
            cat_list.refresh()
        except Exception as e:
            error.set_text(str(e))

    with ui.card() as view_card:
        error=ui.label().classes("text-negative")

        with ui.grid(columns=2):
            ui.input(label="Name").bind_value(cat, 'name')
            ui.number(label="Weight (g)").bind_value(cat, 'weight')
            ui.number(label="Daily quota", min=0, precision=0).bind_value(cat, 'feed_daily')
            ui.number(label="Current quota", precision=3).bind_value(cat, 'feed_quota')

        with ui.card_actions():
            if cat.id is None:
                ui.button(icon="add", on_click=save)
            else:
                delete_button(cat)
                ui.button(icon="save", on_click=save).bind_visibility_from(cat, 'dirty_fields')


@ui.refreshable
def cat_list():
    for cat in DbCat.select():
        cat_card(cat)

    cat_card(DbCat())


@ui.page('/cats')
def overview_page():
    ui_common.header("Cats")
    cat_list()
    ui_common.footer()
