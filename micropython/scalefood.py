import scale
#we want to keep this class independent of IO and display, so we can use it for simulations as well

class ScaleFood(scale.Scale):

    def __init__(self, display=None):

        self.display=display

        #init with course default calibration
        c=[7.61904761904762e-05]
        super().__init__(calibrate_factors=c)

        self.stable_auto_tarre_max=0.1
        self.stable_measurements=3
        self.stable_skip_measurements=3
        self.stable_range=0.1
        self.stable_auto_tarre=600

        # try:
        #     self.load("scale_food.pstate")
        #     print("Loaded scale food")
        # except Exception as e:
        #     print("Error loading scale food:"+str(e))


        self.ate=0
        self.prev_weight=0

    def event_stable(self, timestamp, weight):
        """called once after scale has been stable according to specified stable_ parameters"""
        # print("Stable averaged weight: {}g".format(weight))

        # print(weight, changed, s.offset(s.get_average()))
        # lcd.move_to(0,0)
        # lcd.putstr("{:0.2f}g   \n".format(weight))

        # self.print_debug()
        if self.display:
            self.display.food_weight(weight)

            diff=self.prev_weight-weight
            self.prev_weight=weight
            if abs(diff)<2:
                self.ate=self.ate+diff
                self.display.msg("Ate {:0.2f}g  ".format(self.ate))



        pass
        #calibration weight detected?
        # if not self.state.no_tarre:
        #     for cal in cals:
        #         diff=abs(weight-cal)
        #         if diff< (cal*0.1):
        #             print("Call diff {}g".format(diff))
        #             s.add_calibration(cal)
        # if weight>10:
        #     print("-----")
        #     weights=self.calibrated_weights(self.offset(self.get_average()))
        #     for w in weights:
        #         print(int(w*100/weight))

    def event_realtime(self, timestamp, weight):
        """called on every measurement with actual value (non averaged)"""
        # print("Weight: {}g".format(weight))
        # lcd.move_to(0,1)
        # lcd.putstr("({:0.3f}g)    \n".format(weight))
        pass

    def event_unstable(self, timestamp):
        """called once when scale leaves stable measurement"""
        # print("Unstable")
        # lcd.move_to(0,0)
        # lcd.putstr("          \n")
        if self.display:
            self.display.food_weight_unstable()
        pass
