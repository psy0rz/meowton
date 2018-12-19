import scale
#we want to keep this class independent of IO and display, so we can use it for simulations as well

class ScaleFood(scale.Scale):

    def __init__(self, display, cats):

        # scale configuration
        super().__init__([7.619e-05])
        self.calibrate_weight=10
        self.stable_auto_tarre_max=0.1
        self.stable_auto_tarre=600
        self.stable_measurements=3
        self.stable_skip_measurements=3
        self.stable_range=0.1

        self.display=display
        self.cats=cats

        #to calulate difference between measurements
        self.prev_weight=0

        #keep count as when the cat isnt identified yet
        self.ate=0

        try:
            self.load("scale_food.state")
            print("Loaded scale food")
            self.stable_reset()
        except Exception as e:
            print("Error loading scale food:"+str(e))


    def event_stable(self, weight):
        """called once after scale has been stable according to specified stable_ parameters"""


        diff=self.prev_weight-weight
        self.prev_weight=weight

        if abs(diff)<2:
            if self.cats.current_cat:

                if self.ate:
                    self.cats.current_cat.ate(diff)
                    self.ate=0

                self.cats.current_cat.ate(diff)

                self.display.update_cat(self.cats.current_cat)


            else:
                self.ate=self.ate+diff





        self.display.food_weight_stable(weight)





    def event_realtime(self, weight):
        """called on every measurement with actual value (non averaged)"""

        pass


    def event_unstable(self):
        """called once when scale leaves stable measurement"""

        self.display.food_weight_unstable()


    def msg(self, msg):
        self.display.msg("Food: "+msg)
