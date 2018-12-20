import scale

#we want to keep this class independent of IO and display, so we can use it for simulations as well

class ScaleCat(scale.Scale):

    def __init__(self, display, cats):

        #configure scale
        super().__init__([0.00219]*4)
        self.calibrate_weight=200
        self.stable_auto_tarre_max=1000
        self.stable_auto_tarre=6000

        # self.stable_measurements=25
        # self.stable_skip_measurements=10
        # self.stable_range=50

        self.stable_measurements=12
        self.stable_skip_measurements=5
        self.stable_range=25

        self.display=display
        self.cats=cats

        self.should_save=True

        try:
            self.load("scale_cat.state")
            print("Loaded scale cat")
            self.stable_reset()
        except Exception as e:
            print("Error loading scale cat:"+str(e))

        #always tarre cat scale on boot for nopw
        self.tarre()


    def event_stable(self, weight):
        """called once after scale has been stable according to specified stable_ parameters"""

        #calibrating?
        # if self.calibrating:
        #     self.calibrate(weight)
        #     return

        #update cat weight
        cat=self.cats.by_weight(weight)
        self.cats.select_cat(cat)

        if cat:
            self.should_save=True


        if self.cats.current_cat:
            self.cats.current_cat.update_weight(weight)

        #display stuff
        self.display.scale_weight_stable(weight)
        self.display.update_cat(self.cats.current_cat)




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
