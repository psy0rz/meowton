import time

import settings
from meowton import meowton


def main():

    # load settings
    meowton.load()

    # start
    if settings.headless:
        meowton.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # the program execution will continue here after Ctrl+C
            meowton.stop()
            pass
    else:
        import ui_main
        ui_main.run(meowton.start, meowton.stop)


main()
