import datetime

from nicegui import ui

import ui_common
from food_scheduler import hours_to_list, ScheduleMode
from meowton import meowton


@ui.page('/schedule')
def overview_page():
    def save():
        meowton.food_scheduler.mode = mode.value

        hours = []
        for hour in range(0, 24):
            if hour_checkboxes[hour].value:
                hours.append(hour)
        meowton.food_scheduler.hours = ",".join(map(str, hours))

        meowton.food_scheduler.save()
        ui.notify("saved")
        ui.navigate.back()
        pass

    ui_common.header("Schedule")

    def changed():

        match mode.value:
            case ScheduleMode.UNLIMITED.value:
                description.set_text("Unlimited food, always food in the bowl.")
            case ScheduleMode.SCHEDULED.value:
                description.set_text("Dispense a bit at scheduled times. Keep feeding while detected cat has quota.")
            case ScheduleMode.ALL_QUOTA.value:
                description.set_text(
                    "Dispense a bit at scheduled times when all cats have quota. Keep feeding while detected cat has quota.")
            case ScheduleMode.CAT_QUOTA.value:
                description.set_text("Only feed when detected cat has quota.")
            case ScheduleMode.DISABLED.value:
                description.set_text("Never feed automaticly.")


    ui.label("Feeding mode:")
    mode = ui.toggle(
        {
            ScheduleMode.UNLIMITED.value: "Unlimited",
            ScheduleMode.SCHEDULED.value: "Scheduled",
            ScheduleMode.ALL_QUOTA.value: "All",
            ScheduleMode.CAT_QUOTA.value: "Single",
            ScheduleMode.DISABLED.value: "Disabled"
        }, value=meowton.food_scheduler.mode, on_change=changed).props("dense no-caps")
    description = ui.label("")
    changed()

    ui.separator()
    ui.label("Scheduling hours:")
    hours = hours_to_list(meowton.food_scheduler.hours)
    hour_checkboxes = []
    with ui.grid(columns=4):
        for hour in range(0, 24):
            hour_checkboxes.append(ui.checkbox(str(hour), value=(hour in hours)).props("dense"))

        def select_all():
            for checkbox in hour_checkboxes:
                checkbox.value = True

        def select_none():
            for checkbox in hour_checkboxes:
                checkbox.value = False

        ui.button("All", on_click=select_all).props("flat")
        ui.button("None", on_click=select_none).props("flat")

    now = datetime.datetime.now()
    ui.label(f"(meowton time = {now.strftime('%H:%M')})")
    ui.button(icon="save", on_click=save)

    ui_common.footer()
