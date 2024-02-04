


# from meowton import Meowton
# meowton_instance=Meowton()
# meowton_instance.run()

print("Loading nicegui...")
from nicegui import ui

print("Starting...")

@ui.page('/cats')
def cats_page():
    with ui.header(elevated=True).classes('items-center justify-between'):
        with ui.link(target='/'):
            ui.button(icon='arrow_back').props('flat color=white')
        ui.label('CATS')

    ui.label("hoi")


with ui.header(elevated=True).classes('items-center justify-between'):
    ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
    ui.label('HEADER')
with ui.left_drawer(elevated=True, value=False ) as left_drawer:
    ui.label('LEFT DRAWER')
    with ui.button("Cats"):
        ui.link(target= cats_page)
# with ui.right_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as right_drawer:
#     ui.label('RIGHT DRAWER')
with ui.footer():
    ui.label('FOOTER')



with ui.timeline(side='right'):
    with ui.timeline_entry(
                      title='Mogwai stole 4g in 30 seconds.',
                      subtitle='4 minutes ago', color='red'):
        ui.label("Has to wait 130 minutes for more food.")
        ui.label("Weight: 6.2Kg")
    with ui.timeline_entry(title='Tracy ate 12g in 1 minute',                      subtitle='5 minutes ago'):
        ui.label("Has has 33g left.")
        ui.label("Weight: 3.2Kg")

    with ui.timeline_entry(
                      title='Mogwai ate 6g in 1 minute.',
                      subtitle='15 minutes ago', color='red'):
        ui.label("Has to wait 120 minutes for more food.")
        ui.label("Weight: 6.2Kg")
    with ui.timeline_entry(
                      title='Mogwai sat on the scale for 3 minutes',
                      subtitle='15 minutes ago', color='red'):
        ui.label("Has to wait 120 minutes for more food.")
        ui.label("Weight: 6.2Kg")
    with ui.timeline_entry(
                      title='Mogwai ate 6g',
                      subtitle='15 minutes ago', color='red'):
        ui.label("Has to wait 120 minutes for more food.")
        ui.label("Weight: 6.2Kg")

    with ui.timeline_entry(
                      title='Mogwai ate 8g',
                      subtitle='5 hours ago', color='red'):
        ui.label("Has to wait 65 minutes for more food.")
        ui.label("Weight: 6.2Kg")

    ui.timeline_entry()


ui.run()
