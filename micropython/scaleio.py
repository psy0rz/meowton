import time
import machine
import sys

if sys.platform=='esp32':
    from hx711 import HX711

import config
from lib.state import State


class ScaleIO(State):
    """deals with reading raw loadcell input from HX711 modules"""

    def __init__(self):
        super().__init__()

        
        # self.display=display

        #defaults
        self.state.scale_pins=[[],[],[],[]] # 4 cells
        self.state.food_pins=[[]] #1 cell

        self.state.servo_pin=None
        self.state.servo_fade_time=250
        self.state.servo_sustain_time=183
        self.state.servo_retract_time=0

        self.state.servo_middle_duty=71
        self.state.servo_speed=-20

        self.cells_food=None
        self.cells_cat=None
        self.servo=None

    def start(self):
        """load initial config and configure. raises exceptions on errors"""

        try:
            self.load("scale_io.state")
            print("Loaded scale io config")
        except Exception as e:
            raise(Exception("Error loading scale io config:"+str(e)))

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
            #do this so we actually test the pin and verify it doesnt crash the esp before saving:
            self.servo.duty(self.state.servo_middle_duty);
            time.sleep_ms(60);
            self.servo.duty(0)
        else:
            self.servo=None


    def test(self, cell):
        """test loadcell by detecting noise"""

        # print("Loadcell: Testing with DT={} SCK={}".format(cell.d_out_pin,cell.pd_sck_pin))
        print("Loadcell: Testing with DT={} SCK={}".format(cell.pSCK, cell.pOUT))

        start=cell.read()
        
        # print(start)
        # count=0

        # while start==cell.read():
        #     count=count+1
        #     if count>3:

        if start==0:
            # print("Loadcell: Not found")
            raise(Exception("No cell at pins {},{}".format(cell.pSCK, cell.pOUT)))

        print("Loadcell: Found")


    def _config_loadcells(self, pin_list):
        """swaps pins if needed, returns array of HX711 objects or None when failed"""
        cells=[]
        # try:
        for pins in pin_list:
            if pins[0]==None or pins[1]==None:
                cells.append(None)
            else:
                try:
                    cell=HX711(pins[0], pins[1], 18, gain=128)
                    self.test(cell)
                except:
                    #reverse pins?
                    pins=[ pins[1], pins[0] ]
                    cell=HX711(pins[0], pins[1], 18, gain=128)
                    self.test(cell)
                cells.append(cell)
        return(cells)
        # except Exception as e:
        #     # print("CANT CONFIG PINS {}: {}".format(pins,str(e)))
        #     raise(Exception("Error configuring pins {} ({})".format(pins,str(e))))
        #     # self.display.msg("Loadcell on {} not found!".format(pins))
        #     # return(None)




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
        c=[]
        for cell in self.cells_cat:
            if cell:
                c.append(cell.read())
            else:
                c.append(0)
        # machine.enable_irq(state)
        # print(c)

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
        c=[]
        for cell in self.cells_food:
            if cell:
                c.append(cell.read())
            else:
                c.append(0)
                
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

    def feed(self, test_config=None):
        '''ramp up the feeder, stay there for amount mS, and then ramp back'''

        if not self.servo:
            return

        if not test_config:
            config=self.state
        else:
            config=State()
            config.update_state(test_config) #convert dict to state
            config=config.state
            
   
        #ramp to feed turn
        self._fade(config.servo_middle_duty, config.servo_middle_duty+config.servo_speed, config.servo_fade_time)

        #sustain
        time.sleep_ms(config.servo_sustain_time)

        #ramp to stop
        self._fade(config.servo_middle_duty+config.servo_speed, config.servo_middle_duty, config.servo_fade_time)

        #ramp to retract turn
        if config.servo_retract_time:
            self._fade(config.servo_middle_duty, config.servo_middle_duty-config.servo_speed, config.servo_fade_time)

            #sustain
            time.sleep_ms(config.servo_retract_time)

            #ramp to stop
            self._fade(config.servo_middle_duty-config.servo_speed, config.servo_middle_duty, config.servo_fade_time)

        #disable
        self.servo.duty(0)


    def servo_test(self, config):
        self.servo.duty(config['servo_middle_duty']+config['servo_speed']); #right
        time.sleep_ms(1000);

        self.servo.duty(0) #pauze
        time.sleep_ms(100);

        self.servo.duty(config['servo_middle_duty']-config['servo_speed']); #left
        time.sleep_ms(1000);
        self.servo.duty(0)


    def get_config(self):
        return({
            'selectable_pins': config.selectable_pins,
            'config': self.get_state()
        })

    def update_config(self, config):
        self.update_state(config)
        self.configure()
        #hardware didnt hang so its safe to save now :)
        self.save()

    # def test_servo(self, config):