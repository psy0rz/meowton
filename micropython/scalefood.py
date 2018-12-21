import timer
import scale
#we want to keep this class independent of IO and display, so we can use it for simulations as well

class ScaleFood(scale.Scale):

    def __init__(self, display, cats):

        # scale configuration
        super().__init__([7.619e-05])
        self.calibrate_weight=10
        self.stable_auto_tarre_max=0.1
        self.stable_auto_tarre=600
        self.stable_measurements=2
        self.stable_skip_measurements=2
        self.stable_range=0.2

        self.display=display
        self.cats=cats

        #to calulate difference between measurements
        self.prev_weight=0

        #keep count as when the cat isnt identified yet
        self.ate=0

        self.last_feed=0

        self.just_fed=True

        try:
            self.load("scale_food.state")
            print("Loaded scale food")
            self.stable_reset()
        except Exception as e:
            print("Error loading scale food:"+str(e))


    def fed(self):
        '''indicate we should ignore the current weight change'''
        self.stable_reset()
        self.just_fed=True

    def event_stable(self, weight):
        """called once after scale has been stable according to specified stable_ parameters """


        diff=self.prev_weight-weight
        self.prev_weight=weight

        #ignore weight change after despensing food
        if not self.just_fed:
            if self.cats.current_cat:

                if self.ate:
                    self.cats.current_cat.ate(self.ate)
                    self.ate=0

                self.cats.current_cat.ate(diff)

                self.display.update_cat(self.cats.current_cat)


            else:
                self.ate=self.ate+diff
        else:
            self.just_fed=False





        self.display.food_weight_stable(weight)



        self.print_debug()

    def event_realtime(self, weight):
        """called on every measurement with actual value (non averaged)"""

        pass


    def event_unstable(self):
        """called once when scale leaves stable measurement"""

        self.display.food_weight_unstable()


    def msg(self, msg):
        self.display.msg("Food: "+msg)


    def should_feed(self):
        '''should we put food in the bowl?'''

        #wait between feeds, to prevent mayhem ;)
        if timer.diff(timer.timestamp,self.last_feed)>5000:
            #bowl is stable and empty?
            if self.stable and self.last_stable_weight<0.5:
                # all cats may have food, or current cat may have food?
                if self.cats.quota_all() or ( self.cats.current_cat and self.cats.current_cat.get_quota()>0):
                    self.last_feed=timer.timestamp
                    return True
