import time

from nicegui import ui
from peewee import fn, SQL

import ui_common
from db_cat import DbCat
from db_cat_session import DbCatSession


async def event_list(cat_id: int):
    page_nr = 1
    last_day = 0

    async def check():
        nonlocal page_nr
        nonlocal last_day

        try:
            if await ui.run_javascript('window.pageYOffset >= document.body.offsetHeight - 2 * window.innerHeight'):
                session: DbCatSession
                query = (DbCatSession.select()
                         .where(DbCatSession.cat_id == cat_id)
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


graph=None

def show_graph(cat_id, range_days=30):
    global graph
    now = int(time.time())
    if range_days == 'all':
        time_filter = 0
    else:
        time_filter = now - (int(range_days) * 24 * 60 * 60)

    results = (DbCatSession
               .select(
        fn.DATE(DbCatSession.start_time, 'unixepoch').alias('date'),
        fn.ROUND(fn.MIN(DbCatSession.weight)).alias('min_weight'),
        fn.AVG(DbCatSession.weight).alias('avg_weight'),
        fn.MAX(DbCatSession.weight).alias('max_weight'),
        fn.SUM(DbCatSession.ate).alias('sum_ate')
    )
               .where((DbCatSession.cat == cat_id) & (DbCatSession.start_time >= time_filter))
               .group_by(SQL('date'))
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
                'mode': 'lines+markers',
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
        },
        'config': {
            'displayModeBar': False
        }
    }

    if graph is None:
        graph=ui.plotly(fig)
    else:
        graph.update_figure(fig)


@ui.page("/stats/{cat_id}")
async def page(cat_id):
    cat_id = int(cat_id)
    await ui.context.client.connected()
    title=f"Statistics {DbCat.cats[int(cat_id)].name}"
    ui.page_title(f"Meowton | {title}")
    ui_common.header(title)
    # Add range selector
    range_options = {
        30: "1 month",
        90: "3 months",
        180: "6 months",
        365: "1 year",
        'all': "All",
    }
    with ui.timeline(side='right'):
        range_select = ui.select(
            options=range_options,
            value=list(range_options.keys())[2],
            on_change=lambda e: show_graph(cat_id, e.value)
        )

        global graph
        graph=None
        show_graph(cat_id, range_select.value)

        await event_list(cat_id)
    ui_common.footer()
