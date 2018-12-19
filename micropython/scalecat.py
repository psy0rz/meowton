import scale

#we want to keep this class independent of IO and display, so we can use it for simulations as well

class ScaleCat(scale.Scale):

    def __init__(self, display, cats):

        #configure scale
        super().__init__([0.00219]*4)
        self.calibrate_weight=200
        self.stable_auto_tarre_max=1000
        self.stable_auto_tarre=6000
        self.stable_measurements=25
        self.stable_skip_measurements=10
        self.stable_range=50

        self.display=display
        self.cats=cats


        try:
            self.load("scale_cat.state")
            print("Loaded scale cat")
            self.stable_reset()
        except Exception as e:
            print("Error loading scale cat:"+str(e))


    def event_stable(self, weight):
        """called once after scale has been stable according to specified stable_ parameters"""

        #calibrating?
        # if self.calibrating:
        #     self.calibrate(weight)
        #     return

        #update cat weight
        cat=self.cats.by_weight(weight)
        self.cats.select_cat(cat)

        if self.cats.current_cat:
            self.cats.current_cat.update_weight(weight)

        #display stuff
        self.display.scale_weight_stable(weight)
        self.display.update_cat(self.cats.current_cat)



    # def calibrate(self, weight):
    #     averages=self.offset(self.get_average())
    #     weights=self.calibrated_weights(averages)
    #     zeros=0
    #     factor=0
    #     for sensor in range(0,self.sensor_count):
    #         if abs(weights[sensor])<1:
    #             zeros=zeros+1
    #         if weights[sensor]>10:
    #             factor=self.calibrate_weight/averages[sensor]
    #             cal_sensor=sensor
    #
    #     if zeros==self.sensor_count-1 and factor:
    #         self.display.msg("Calibrated #{}".format(cal_sensor))
    #         self.state.calibrate_factors[cal_sensor]=factor
    #
    #         #done?
    #         for factor in self.state.calibrate_factors:
    #             #Note: there is no way a cell calibrates exactly on this factor :)
    #             if factor==self.default_factor:
    #                 return
    #
    #         self.calibrating=False
    #         self.display.msg("Calibration done")
    #         self.save()
    #     else:
    #         self.display.msg("Cal. place {}g ".format(self.calibrate_weight))


    # def recalibrate(self):
    #     self.calibrating=True
    #     #reset to default cal
    #     c=[self.default_factor] * 4
    #     self.state.calibrate_factors=c
    #     self.tarre(0)



    def event_realtime(self, weight):
        """called on every measurement with actual value (non averaged)"""
        pass


    def event_unstable(self):
        """called once when scale leaves stable measurement"""

        self.cats.select_cat(None)

        self.display.scale_weight_unstable()
        pass

    def msg(self, msg):
        self.display.msg("Scale: "+msg)
