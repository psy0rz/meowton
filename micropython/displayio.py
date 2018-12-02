
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

class DisplayIO():

    def __init__(self):
        DEFAULT_I2C_ADDR = 0x27
        self.i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
        self.lcd = I2cLcd(self.i2c, DEFAULT_I2C_ADDR, 2, 16)
