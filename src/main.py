import asyncio
import time

import settings
from meowton import meowton


def main():


    import ui_main
    ui_main.run(meowton.start, meowton.stop )


main()



