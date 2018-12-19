
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


    def scale_weight_stable(self, weight):
        self.lcd.move_to(0,0)
        s="  Scale: {:0.0f}g    ".format(weight)
        self.lcd.putstr(s)

    def scale_weight_unstable(self):
        self.lcd.move_to(0,0)
        self.lcd.putstr("*")


    def food_weight_stable(self, weight):
        self.lcd.move_to(0,1)
        s="  Food : {:0.2f}g    ".format(weight)
        self.lcd.putstr(s)

    def food_weight_unstable(self):
        self.lcd.move_to(0,1)
        self.lcd.putstr("*")


    def update_cat(self, cat):
        self.lcd.move_to(0,2)
        if cat:
            self.lcd.putstr("{}: {:0.0f}g ({:0.0f})".format(cat.state.name, cat.state.weight, cat.get_quota()))
        else:
            self.lcd.putstr("                ")



    def msg(self, txt):
        self.lcd.move_to(0,3)
        self.lcd.putstr(txt+"  ")
