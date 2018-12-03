import scale

#we want to keep this class independent of IO and display, so we can use it for simulations as well

class ScaleCat(scale.Scale):

    def __init__(self, display=None):

        self.display=display

        #init with default course calibration
        self.calibrating=False
        self.calibrate_weight=200
        self.default_factor=0.002192447149507885
        c=[self.default_factor] * 4
        super().__init__(calibrate_factors=c)


        self.stable_auto_tarre_max=1000
        self.stable_auto_tarre=100

        self.stable_measurements=25
        self.stable_skip_measurements=10
        self.stable_range=50

        self.stable_measurements=5
        self.stable_skip_measurements=5
        self.stable_range=10

        try:
            self.state.load("scale_cat.state")
            print("Loaded scale cat")
        except Exception as e:
            print("Error loading scale cat:"+str(e))
            self.recalibrate()


    def event_stable(self, timestamp, weight):
        """called once after scale has been stable according to specified stable_ parameters"""
        # print("Stable averaged weight: {}g".format(weight))

        # print(weight, changed, s.offset(s.get_average()))
        # lcd.move_to(0,0)
        # lcd.putstr("{:0.1f}g   \n".format(weight))
        if self.display:
            self.display.cat_weight(weight)


        #calibrating?
        if self.calibrating:
            self.calibrate(weight)
            return

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

    def calibrate(self, weight):
        averages=self.offset(self.get_average())
        weights=self.calibrated_weights(averages)
        zeros=0
        factor=0
        for sensor in range(0,self.sensor_count):
            if abs(weights[sensor])<1:
                zeros=zeros+1
            if weights[sensor]>10:
                factor=self.calibrate_weight/averages[sensor]
                cal_sensor=sensor

        if zeros==self.sensor_count-1 and factor:
            self.display.msg("Calibrated #{}".format(cal_sensor))
            self.state.calibrate_factors[cal_sensor]=factor

            #done?
            for factor in self.state.calibrate_factors:
                #Note: there is no way a cell calibrates exactly on this factor :)
                if factor==self.default_factor:
                    return

            self.calibrating=False
            self.display.msg("Calibration done")
            self.state.save()


    def recalibrate(self):
        self.calibrating=True
        #reset to default cal
        c=[self.default_factor] * 4
        self.state.calibrate_factors=c
        self.tarre(0)
        self.display.msg("Cal. place {}g ".format(self.calibrate_weight))



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
