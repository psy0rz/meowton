import time
import machine
from hx711 import HX711
import config
from lib.state import State


class ScaleIO(State):
    """deals with reading raw loadcell input from HX711 modules"""

    def __init__(self, display):
        super().__init__()

        self.display=display

        try:
            self.load("scale_io.state")
            print("Loaded scale io config")
            self.stable_reset()
        except Exception as e:
            print("Error loading scale io config:"+str(e))
            #defaults
            self.state.scale_pins=[[],[],[],[]] # 4 cells
            self.state.food_pins=[]

            self.state.servo_pin=None
            self.state.servo_fade_time=300
            self.state.servo_sustain_time=300
            self.state.servo_retract_time=100

        self.configure()

    def configure(self):
        """(re)configure hardware """

        ### config cat scale pins
        self.cells_cat=self._config_loadcells(self.state.scale_pins)

        ### config food scale pins
        self.cells_food=self._config_loadcells(self.state.food_pins)


        ### config servo
        # self.servo = machine.PWM(machine.Pin(17), freq=50)
        if self.state.servo_pin:
            self.servo = machine.PWM(machine.Pin(self.state.servo_pin), freq=50)
            self.servo.duty(0)
        else:
            self.servo=None


    def test(self, cell):
        """test loadcell by detecting noise"""

        # print("Loadcell: Testing with DT={} SCK={}".format(cell.d_out_pin,cell.pd_sck_pin))
        print("Loadcell: Testing with DT={} SCK={}".format(cell.pSCK, cell.pOUT))

        start=cell.read()
        count=0

        while start==cell.read():
            count=count+1
            if count>3:
                return(False)

        print("Loadcell: Found")
        return(True)


    def _config_loadcells(self, pin_list):
        """swaps pins if needed, returns array of HX711 objects or None when failed"""
        cells=[]
        try:
            for pins in pin_list:
                cell=HX711(pins[0], pins[1], 18, gain=128)
                if not self.test(cell):
                    #reverse pins?
                    pins=[ pins[1], pins[0] ]
                    cell=HX711(pins[0], pins[1], 18)
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




    def scales_ready(self):
        

        if self.cells_food and not self.cells_food[0].is_ready():
            # print("food not ready")
            return False

        if self.cells_cat:
            for cell in self.cells_cat:
                if not cell.is_ready():
                    # print("cell not ready="+str(cell.d_out_pin))
                    return False

        return True


    def read_cat(self):
        if not self.cells_cat:
            return None

        # state=machine.disable_irq()
        c=[         self.cells_cat[0].read(),
                    self.cells_cat[1].read(),
                    self.cells_cat[2].read(),
                    self.cells_cat[3].read()]
        # machine.enable_irq(state)

        read_error=False
        for i in range(0,len(c)):
            # if abs(self.prev_cat_sensor[i]-c[i])>100000:
            if c[i]==-1:
                print("read-error scale")
                read_error=True
            # self.prev_cat_sensor[i]=c[i]

        if not read_error:
            return(c)
        else:
            return(False)


    def read_food(self):
        if not self.cells_food:
            return None

        # state=machine.disable_irq()
        c=[
            self.cells_food[0].read(),
        ]
        # machine.enable_irq(state)

        # diff=abs(self.prev_food_sensor-c[0])
        # self.prev_food_sensor=c[0]

        # if diff<100000:
        if c[0]!=-1:
            return(c)
        else:
            print("read error food")
            return(False)



    def _fade(self, start_duty, end_duty, fade_time):
        '''pwm duty-cycle fader'''
        start_time=time.ticks_ms()
        passed_time=0
        while passed_time<fade_time:
            value=int(start_duty + (end_duty-start_duty)*(passed_time/fade_time))
            self.servo.duty(value)
            passed_time=time.ticks_diff(time.ticks_ms(),start_time)

        self.servo.duty(end_duty)

    def feed(self):
        '''ramp up the feeder, stay there for amount mS, and then ramp back'''

        if not self.servo:
            return

        #TODO: make configurable?
        left_duty=90
        middle_duty=77
        # right_duty=67
        right_duty=60

        #ramp to right turn
        self.fade(middle_duty, right_duty, self.state.servo_fade_time)

        #sustain
        time.sleep_ms(self.state.servo_sustain_time)

        #ramp to stop
        self.fade(right_duty, middle_duty, self.state.servo_fade_time)

        #ramp to left turn
        self.fade(middle_duty, left_duty, self.state.servo_fade_time)

        #sustain
        time.sleep_ms(self.state.servo_retract_time)

        #ramp to stop
        self.fade(left_duty, middle_duty, self.state.servo_fade_time)


        #disable
        self.servo.duty(0)


    def get_config(self):
        return({
            'selectable_pins': config.selectable_pins,
            'config': self.get_state()
        })

