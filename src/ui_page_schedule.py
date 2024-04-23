import datetime

from nicegui import ui

import ui_common
from food_scheduler import hours_to_list
from meowton import meowton


@ui.page('/schedule')
def overview_page():
    def save():
        meowton.food_scheduler.feed_on_schedule = feed_on_schedule.value
        meowton.food_scheduler.feed_unlimited = feed_unlimited.value
        meowton.food_scheduler.feed_when_quota = feed_when_quota.value

        hours=[]
        for hour in range(0,24):
            if hour_checkboxes[hour].value:
                hours.append(hour)
        meowton.food_scheduler.hours = ",".join(map(str,hours))

        meowton.food_scheduler.save()
        ui.notify("saved")
        ui.navigate.back()
        pass

    ui_common.header("Schedule")

    with ui.checkbox("Unlimited food", value=meowton.food_scheduler.feed_unlimited) as feed_unlimited:
        ui.label("Always keeps food in the bowl. Ignores quotas and feed times.").classes("text-grey")

    with ui.checkbox("Feed on schedule", value=meowton.food_scheduler.feed_on_schedule) as feed_on_schedule:
        feed_on_schedule.bind_enabled_from(feed_unlimited, 'value', backward=lambda v: not v)
        ui.label("Dispense a portion at schedule times. Ignoring quotas.").classes("text-grey")

    with ui.checkbox("Feed when quota", value=meowton.food_scheduler.feed_when_quota) as feed_when_quota:
        feed_when_quota.bind_enabled_from(feed_unlimited, 'value', backward=lambda v: not v)
        ui.label("Dispense a portion as soon as all cats have quota.").classes("text-grey")


    ui.label("Schedule:")
    hours=hours_to_list(meowton.food_scheduler.hours)
    hour_checkboxes=[]
    with ui.grid(columns=4):
        for hour in range(0,24):
            hour_checkboxes.append(ui.checkbox(str(hour), value=(hour in hours)))

        def select_all():
            for checkbox in hour_checkboxes:
                checkbox.value=True

        def select_none():
            for checkbox in hour_checkboxes:
                checkbox.value=False

        ui.button("All", on_click=select_all).props("flat")
        ui.button("None", on_click=select_none).props("flat")

    now=datetime.datetime.now()
    ui.label(f"(server time = { now.strftime('%H:%M')})")
    ui.button(icon="save", on_click=save)

    ui_common.footer()
