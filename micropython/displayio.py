
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

class DisplayIO():

    def __init__(self):
        DEFAULT_I2C_ADDR = 0x27
        self.i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)

        self.cols=20
        self.rows=4
        # 2x16
        # self.lcd = I2cLcd(self.i2c, DEFAULT_I2C_ADDR, 2, 16)

        # 4x16
        self.lcd = I2cLcd(self.i2c, DEFAULT_I2C_ADDR, self.rows, self.cols)

        self.last_cat=""
        self.cat_row=2


    def scale_weight_stable(self, weight):
        self.lcd.move_to(0,0)
        s=" {:4.0f}g cat".format(weight)
        s="{:<10}".format(s)
        self.lcd.putstr(s)

    def scale_weight_unstable(self):
        self.lcd.move_to(0,0)
        self.lcd.putstr("*")


    def food_weight_stable(self, weight):
        self.lcd.move_to(11,0)
        s=" {:2.0f}g food".format(weight)
        s="{:<10}".format(s)
        self.lcd.putstr(s)

    def food_weight_unstable(self):
        self.lcd.move_to(11,0)
        self.lcd.putstr("*")


    def update_cat(self, cat):

        if cat:
            if cat.state.name!=self.last_cat:
                self.last_cat=cat.state.name
                self.cat_row=self.cat_row+1
                if self.cat_row>3:
                    self.cat_row=2

            s="{:<8} {:4.0f}g ({:3.0f})".format(cat.state.name[:8], cat.state.weight, cat.get_quota())
            s="{:<20}".format(s)

            self.lcd.move_to(0,self.cat_row)
            self.lcd.putstr(s)



    def msg(self, txt):
        self.lcd.move_to(0,2)
        self.lcd.putstr("{:<20}".format(txt))
