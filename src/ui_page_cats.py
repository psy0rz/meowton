import peewee
from nicegui import ui

import ui_common
import ui_main
from db_cat import DbCat


def delete_button(cat: DbCat):
    def confirmed():
        cat.delete_instance()
        cat_list.refresh()
        ui_main.main_page.refresh()

    def click():
        ui_common.confirm(message=f"Delete cat {cat.name} ?", on_confirm=confirmed)

    ui.button(icon="delete", on_click=click).props("color=red")


def cat_card(cat: DbCat):
    def save():
        try:
            cat.name=name.value
            cat.feed_quota=feed_quota.value
            cat.feed_daily=feed_daily.value
            cat.weight=weight.value
            cat.save()
            cat_list.refresh()
            ui_main.main_page.refresh()
            ui.notify(f"Cat {cat.name} saved")
        except Exception as e:
            error.set_text(str(e))

    with ui.card() as view_card:
        error=ui.label().classes("text-negative")

        with ui.grid(columns=2):
            name=ui.input(label="Name", value=cat.name)
            weight=ui.number(label="Weight (g)", format='%.0f', value=cat.weight)
            feed_quota=ui.number(label="Current quota", format='%0.2f', value=cat.feed_quota)
            feed_daily=ui.number(label="Daily quota", min=0, precision=0, value=cat.feed_daily)

        with ui.card_actions():
            if cat.id is None:
                ui.button(icon="add", on_click=save)
            else:
                delete_button(cat)
                ui.button(icon="save", on_click=save)


@ui.refreshable
def cat_list():
    for cat in DbCat.cats.values():
        cat_card(cat)

    cat_card(DbCat())


@ui.page('/cats')
def overview_page():
    ui_common.header("Cats")
    cat_list()
    ui_common.footer()
