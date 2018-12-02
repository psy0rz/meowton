
from hx711 import HX711

class ScaleIO():
    """deals with reading raw loadcell input from HX711 modules"""

    def __init__(self):
        self.cells_cat=[
            HX711(d_out=34, pd_sck=32), #1
            HX711(d_out=25, pd_sck=33), #2
            HX711(d_out=27, pd_sck=26), #3
            HX711(d_out=17, pd_sck=5), #4
        ]

        self.cells_food=[ HX711(d_out=14, pd_sck=12) ]


    def read_cat(self):
        return([
            self.cells_cat[0].read(),
            self.cells_cat[1].read(),
            self.cells_cat[2].read(),
            self.cells_cat[3].read(),
        ])


    def read_food(self):
        return([
            self.cells_food[0].read(),
        ])
