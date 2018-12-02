import scale

#we want to keep this class independent of IO and display, so we can use it for simulations as well

class ScaleCat(scale.Scale):

    def __init__(self, display=None):

        self.display=display

        #init with default course calibration
        avg=0.002192447149507885
        c=[avg] * 4
        super().__init__(calibrate_factors=c)

        self.stable_auto_tarre_max=1000
        self.stable_measurements=25
        self.stable_skip_measurements=10
        self.stable_range=50
        self.stable_auto_tarre=100

        try:
            scale_cat.state.load("scale_cat.state")
            print("Loaded scale cat")
        except Exception as e:
            print("Error loading scale cat:"+str(e))


    def event_stable(self, timestamp, weight):
        """called once after scale has been stable according to specified stable_ parameters"""
        # print("Stable averaged weight: {}g".format(weight))

        # print(weight, changed, s.offset(s.get_average()))
        # lcd.move_to(0,0)
        # lcd.putstr("{:0.1f}g   \n".format(weight))
        if self.display:
            self.display.cat_weight(weight)

        self.print_debug()
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
        # lcd.putstr("({:0.1f}g)    \n".format(weight))
        pass


    def event_unstable(self, timestamp):
        """called once when scale leaves stable measurement"""
        # print("Unstable")
        # lcd.move_to(0,0)
        # lcd.putstr("          \n")
        if self.display:
            self.display.cat_weight_unstable()
        pass
