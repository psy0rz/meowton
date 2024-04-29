import time

from nicegui import ui

import ui_common
from db_cat import DbCat
from db_cat_session import DbCatSession


async def event_list(id: int):
    page_nr = 0
    last_day=0

    async def check():
        nonlocal page_nr
        nonlocal last_day

        try:
            if await ui.run_javascript('window.pageYOffset >= document.body.offsetHeight - 2 * window.innerHeight'):
                session: DbCatSession
                query = (DbCatSession.select()
                         .where(DbCatSession.cat_id == id)
                         .order_by(DbCatSession.start_time.desc())
                         .paginate(page_nr, 10))

                for session in query:

                    t=time.localtime(session.start_time)

                    if t.tm_yday!=last_day:
                        last_day=t.tm_yday
                        with ui.timeline_entry(heading=True):
                            date_str=time.strftime("%A, %d %B", t)
                            ui.label(f"{date_str}").classes("text-h6")

                    if session.ate < 0.1:
                        title = f"{session.cat.name} waited for {session.length}s"
                    else:
                        title = f"{session.cat.name} ate {session.ate:0.1f}g in {session.length}s"

                    time_str = time.ctime(session.start_time)

                    with ui.timeline_entry(title=title, subtitle=time.strftime("%H:%M",t)):
                        ui.label(f"Max weight: {session.weight:0.0f}g")

                page_nr += 1
        except TimeoutError:
            pass

    await ui.context.client.connected()

    t = ui.timer(1, check)


@ui.page("/stats/{id}")
async def page(id):
    id = int(id)

    ui_common.header(f"Statistics {DbCat.cats[int(id)].name}")
    ui_common.footer()
    with ui.timeline(side='right'):
        await event_list(id)
