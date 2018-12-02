
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

class DisplayIO():

    def __init__(self):
        DEFAULT_I2C_ADDR = 0x27
        self.i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)

        # 2x16
        # self.lcd = I2cLcd(self.i2c, DEFAULT_I2C_ADDR, 2, 16)

        # 4x16
        self.lcd = I2cLcd(self.i2c, DEFAULT_I2C_ADDR, 4, 16)


    def cat_weight(self, weight, stable):
        self.lcd.move_to(0,0)
        s="Scale: {:0.0f}g ".format(weight)
        if not stable:
            s=s+"*"
        s=s+"     "
        self.lcd.putstr(s)

    def food_weight(self, weight, stable):
        self.lcd.move_to(0,1)
        s="Food : {:0.2f}g ".format(weight)
        if not stable:
            s=s+"*"
        s=s+"     "
        self.lcd.putstr(s)
