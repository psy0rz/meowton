import time
import machine
from hx711 import HX711
import config

class ScaleIO():
    """deals with reading raw loadcell input from HX711 modules"""

    def test(self, cell):
        """test loadcell by detecting noise"""

        print("Loadcell: Testing with DT={} SCK={}".format(cell.d_out_pin,cell.pd_sck_pin))

        start=cell.read()
        count=0

        while start==cell.read():
            count=count+1
            if count>3:
                return(False)

        print("Loadcell: Found")
        return(True)


    def config_loadcells(self, pin_list):
        """tests and config loadcells, returns array of HX711 objects or None when failed"""
        cells=[]
        try:
            for pins in pin_list:
                cell=HX711(*pins)
                if not self.test(cell):
                    #reverse pins?
                    pins=[ pins[1], pins[0] ]
                    cell=HX711(*pins)
                    if not self.test(cell):
                        # print("NOT FOUND {}".format(pins))
                        self.display.msg("Loadcell on {} not found!".format(pins))
                        return(None)
                cells.append(cell)
            return(cells)
        except Exception as e:
            print("CANT CONFIG PINS {}: {}".format(pins,str(e)))
            self.display.msg("Loadcell on {} not found!".format(pins))
            return(None)


    def __init__(self, display):
        self.display=display
        # self.display.msg("Scale IO init")


        ### config cat scale pins
        self.cells_cat=self.config_loadcells(config.scale_pins)

        ### config food scale pins
        self.cells_food=self.config_loadcells(config.food_pins)


        ### config servo
        # self.servo = machine.PWM(machine.Pin(17), freq=50)
        self.servo = machine.PWM(machine.Pin(config.servo_pin), freq=50)
        self.servo.duty(0)


    def scales_ready(self):
        if self.cells_food and not self.cells_food[0].is_ready():
            return False

        if self.cells_cat:
            for cell in self.cells_cat:
                if not cell.is_ready():
                    return False

        return True


    def read_cat(self):
        if not self.cells_cat:
            return None

        state=machine.disable_irq()
        c=[         self.cells_cat[0].read(),
                    self.cells_cat[1].read(),
                    self.cells_cat[2].read(),
                    self.cells_cat[3].read()]
        machine.enable_irq(state)

        return(c)


    def read_food(self):
        if not self.cells_food:
            return None

        state=machine.disable_irq()
        c=[
            self.cells_food[0].read(),
        ]
        machine.enable_irq(state)
        return(c)



    def fade(self, pwm, start_duty, end_duty, fade_time):
        '''pwm duty-cycle fader'''
        start_time=time.ticks_ms()
        passed_time=0
        while passed_time<fade_time:
            value=int(start_duty + (end_duty-start_duty)*(passed_time/fade_time))
            pwm.duty(value)
            passed_time=time.ticks_diff(time.ticks_ms(),start_time)

        pwm.duty(end_duty)

    def feed(self, fade_time, sustain_time, retract_time):
        '''ramp up the feeder, stay there for amount mS, and then ramp back'''

        left_duty=90
        middle_duty=77
        # right_duty=67
        right_duty=60
        self.servo.duty(0)

        #feed
        self.fade(self.servo, middle_duty, right_duty, fade_time)

        self.servo.duty(right_duty)
        time.sleep_ms(sustain_time)

        #retract
        self.servo.duty(left_duty)
        time.sleep_ms(retract_time)

        #disable
        self.servo.duty(0)



        # #feed
        # self.fade(self.servo, middle_duty, right_duty, 100)
        # time.sleep_ms(amount)
        #
        # self.fade(self.servo, right_duty, middle_duty, 100)
        #
        # # ### retract
        # self.fade(self.servo, middle_duty, left_duty, 100)
        # self.fade(self.servo, left_duty, middle_duty, 100)
        #
        # #disable
        # self.servo.duty(0)
