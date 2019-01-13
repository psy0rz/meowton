import timer
import display
import config
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

class Display(display.Display):
    """standard LCD2004 20x4 display via I2C"""

    def __init__(self):
        super().__init__()

        DEFAULT_I2C_ADDR = 0x27
        self.i2c = I2C(scl=Pin(config.lcd_pins[1]), sda=Pin(config.lcd_pins[0]), freq=400000)

        self.cols=20
        self.rows=4
        # 2x16
        # self.lcd = I2cLcd(self.i2c, DEFAULT_I2C_ADDR, 2, 16)

        # 4x16
        self.lcd = I2cLcd(self.i2c, DEFAULT_I2C_ADDR, self.rows, self.cols)

        self.cats=[]
        self.msg_timeout=0


    def scale_weight_stable(self, weight):
        """called when a stable weight is detected on the cat scale """
        self.lcd.move_to(0,0)
        s=" {:4.0f}g".format(weight)
        s="{:<10}".format(s)
        self.lcd.putstr(s)

    def scale_weight_unstable(self):
        """called when cat scale starts moving """
        self.lcd.move_to(0,0)
        self.lcd.putstr("*")


    def food_weight_stable(self, weight):
        """called when a stable weight is detected on the food scale """
        self.lcd.move_to(11,0)
        s=" {:2.2f}g".format(weight)
        s="{:<9}".format(s)
        self.lcd.putstr(s)

    def food_weight_unstable(self):
        """called when food scale starts moving """
        self.lcd.move_to(11,0)
        self.lcd.putstr("*")


    def update_cat(self, cat):
        """called to update info about currently detected cat. called with None if cat has left"""

        # if cat:
        #     if cat.state.name!=self.last_cat:
        #         self.last_cat=cat.state.name
        #         self.cat_row=self.cat_row+1
        #         if self.cat_row>3:
        #             self.cat_row=2
        if cat and cat not in self.cats:
            self.cats.append(cat)

            #max 2 cats on display
            self.cats=self.cats[-2:]


    def refresh(self):
        """called every second to update/refresh info on screen"""
        self.lcd.move_to(0,2)
        for cat in self.cats:
            if cat.state.weight:
                # s="{:<6} {:4.0f}g {:7.3f}".format(cat.state.name[:8], cat.state.weight,  cat.get_quota())
                s="{:<6} {:4.0f}g {:5.0f}m".format(cat.state.name[:8], cat.state.weight, cat.time())
                s="{:<20}".format(s)
                self.lcd.putstr(s)

        if self.msg_timeout and timer.diff(timer.timestamp,self.msg_timeout)>0:
            self.lcd.move_to(0,1)
            self.lcd.putstr("{:<20}".format(""))
            self.msg_timeout=None




    def msg(self, txt, timeout=10):
        """called to display a message on the screen"""
        self.lcd.move_to(0,3)
        self.lcd.putstr("{:<20}".format(txt[:20]))
        if timeout:
            self.msg_timeout=timer.add(timer.timestamp, timeout*1000)
        else:
            self.msg_timeout=None
