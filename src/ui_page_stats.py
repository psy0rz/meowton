import time

from nicegui import ui

from db_cat_session import DbCatSession


@ui.page("/stats/{id}")
async def page(id):
    page_nr = 0


    # async def check():
    #
    #
    #     if await ui.run_javascript('window.pageYOffset >= document.body.offsetHeight - 2 * window.innerHeight'):
    #         for session in DbCatSession.select().paginate(page_nr, 5):
    #             with ui.card():
    #                 ui.label(session.cat.name)
    #
    #         page_nr += 1
    #
    # await ui.context.client.connected()
    #
    # t = ui.timer(1, check)
