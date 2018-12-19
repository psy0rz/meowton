import machine
from hx711 import HX711

class ScaleIO():
    """deals with reading raw loadcell input from HX711 modules"""

    def __init__(self):
        self.cells_cat=[
            HX711(d_out=34, pd_sck=32), #1
            HX711(d_out=25, pd_sck=33), #2
            HX711(d_out=27, pd_sck=26), #3
            # HX711(d_out=4, pd_sck=5), #4
            # HX711(d_out=23, pd_sck=5), #4
            # HX711(d_out=18, pd_sck=5,), #4
            # HX711(d_out=18, pd_sck=23), #4
            HX711(d_out=23, pd_sck=18), #4
        ]

        self.cells_food=[ HX711(d_out=14, pd_sck=12) ]

    def scales_ready(self):
        if not self.cells_food[0].is_ready():
            return False

        for cell in self.cells_cat:
            if not cell.is_ready():
                return False

        return True

    def read_cat(self):
        state=machine.disable_irq()
        c=[         self.cells_cat[0].read(),
                    self.cells_cat[1].read(),
                    self.cells_cat[2].read(),
                    self.cells_cat[3].read()]
        machine.enable_irq(state)

        return(c)


    def read_food(self):
        state=machine.disable_irq()
        c=[
            self.cells_food[0].read(),
        ]
        machine.enable_irq(state)
        return(c)
