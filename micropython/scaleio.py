import time
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

        # self.servo = machine.PWM(machine.Pin(17), freq=50)
        self.servo = machine.PWM(machine.Pin(13), freq=50)
        self.servo.duty(0)
#

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



    def fade(self, pwm, start_duty, end_duty, fade_time):
        '''pwm duty-cycle fader'''
        start_time=time.ticks_ms()
        passed_time=0
        while passed_time<fade_time:
            value=int(start_duty + (end_duty-start_duty)*(passed_time/fade_time))
            pwm.duty(value)
            passed_time=time.ticks_diff(time.ticks_ms(),start_time)

        pwm.duty(end_duty)

    def feed(self, amount):
        '''ramp up the feeder, stay there for amount mS, and then ramp back'''

        left_duty=90
        middle_duty=77
        right_duty=60
        self.servo.duty(0)

        #feed
        self.fade(self.servo, middle_duty, right_duty, 100)
        time.sleep_ms(amount)

        self.fade(self.servo, right_duty, middle_duty, 100)

        # ### retract
        self.fade(self.servo, middle_duty, left_duty, 100)
        self.fade(self.servo, left_duty, middle_duty, 100)

        #disable
        self.servo.duty(0)
