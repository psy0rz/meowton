import time
import machine
from hx711 import HX711
import config

class ScaleIO():
    """deals with reading raw loadcell input from HX711 modules"""

    def test(self, cell):
        """test loadcell by detecting noise"""

        start=cell.read()
        count=0

        while start==cell.read():
            count=count+1
            if count>10:
                raise(Exception("No noise detected (value={})".format(start)))


    def __init__(self, display):
        self.display=display
        # self.display.msg("Scale IO init")

        self.cells_cat=[]

        try:
            cell_nr=0
            for pins in config.scale_pins:
                cell_nr=cell_nr+1
                # self.display.msg("Scale init cell {}".format(cell_nr))
                cell=HX711(*pins)
                self.test(cell)
                self.cells_cat.append(cell)
        except Exception as e:
            #disable
            self.display.msg("IO error on cell {} ({}: {})".format(cell_nr, e.__class__.__name__, str(e)))
            self.cells_cat=None


        try:
            cell=HX711(*config.food_pins)



            self.test(cell)
            self.cells_food=[ cell ]
        except Exception as e:
            #disable
            self.cells_food=None
            self.display.msg("IO error on food cell ({}: {})".format(e.__class__.__name__, str(e)))


        # self.servo = machine.PWM(machine.Pin(17), freq=50)
        self.servo = machine.PWM(machine.Pin(13), freq=50)
        self.servo.duty(0)
#

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
