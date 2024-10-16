import time

from nicegui import ui
from peewee import fn, SQL

import ui_common
from db_cat import DbCat
from db_cat_session import DbCatSession


async def event_list(id: int):
    page_nr = 1
    last_day = 0

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

                    t = time.localtime(session.start_time)

                    if t.tm_yday != last_day:
                        last_day = t.tm_yday
                        with ui.timeline_entry(heading=True):
                            date_str = time.strftime("%A, %d %B", t)
                            ui.label(f"{date_str}").classes("text-h6")

                    if session.ate < 0.1:
                        title = f"{session.cat.name} waited for {session.length}s"
                        icon = "no_meals"
                        color = "red"
                    else:
                        title = f"{session.cat.name} ate {session.ate:0.1f}g in {session.length}s"
                        icon = "restaurant"
                        color = None

                    time_str = time.ctime(session.start_time)

                    with ui.timeline_entry(title=title, subtitle=time.strftime("%H:%M", t), icon=icon, color=color):
                        ui.label(f"Max weight: {session.weight:0.0f}g")

                page_nr += 1
        except TimeoutError:
            pass


    t = ui.timer(1, check)


def show_graph(id):
    results = (DbCatSession
               .select(
        fn.DATE(DbCatSession.start_time, 'unixepoch').alias('date'),
        fn.ROUND(fn.MIN(DbCatSession.weight)).alias('min_weight'),
        fn.AVG(DbCatSession.weight).alias('avg_weight'),
        fn.MAX(DbCatSession.weight).alias('max_weight'),
        fn.SUM(DbCatSession.ate).alias('sum_ate')
    )
               .where(DbCatSession.cat == id)
               .group_by(SQL('date'))  # Use SQL function to refer to the alias
               )

    dates = []
    avg_weights = []
    min_weights = []
    max_weights = []
    sum_ates = []

    for record in results:

        dates.append(record.date)
        avg_weights.append(record.avg_weight)
        min_weights.append(record.min_weight)
        max_weights.append(record.max_weight)
        sum_ates.append(record.sum_ate)

    fig = {
        'data': [
            {
                'x': dates,
                'y': min_weights,

                'mode': 'line',
                'name': 'Min Weight',
                'line': {
                    'shape': 'spline',
                    'color': '#00000000',
                },
            },
            {
                'x': dates,
                'y': max_weights,
                'mode': 'line',
                'name': 'Max Weight',
                'line': {
                    'shape': 'spline',
                    'color': '#00000000',
                },
                'fill': 'tonexty',
                'fillcolor': '#00000011'
            },
            {
                'x': dates,
                'y': avg_weights,
                'mode': 'line',
                'name': 'Average Weight',
                'line': {'shape': 'linear'},
            },
            {
                'x': dates,
                'y': sum_ates,
                'yaxis': 'y2',
                'name': 'Food',
                'mode': 'markers',
                'line': {
                    'shape': 'linear',
                    'color': '#ff000050',

                },
            },

        ],
        'layout': {
            'title': 'Daily Weight Statistics',
            'xaxis': {'title': 'Date'},
            'yaxis': {
                'title': 'Weight (g)'
            },
            'yaxis2': {
                'title': 'Food (g)',
                'side': 'right',
                'overlaying': 'y'
            },
            'showlegend': False,
            'clickmode': False,
            'dragmode': False,
            'margin':{
                'b': 40,
                't': 40,
                'l': 50,
                'r': 40

            }
        }
        , 'config': {
            'displayModeBar': False
        }
    }
    ui.plotly(fig)


@ui.page("/stats/{id}")
async def page(id):
    id = int(id)

    await ui.context.client.connected()

    title=f"Statistics {DbCat.cats[int(id)].name}"
    ui.page_title(f"Meowton | {title}")


    ui_common.header(title)
    ui_common.footer()

    with ui.timeline(side='right'):
        show_graph(id)
        await event_list(id)
