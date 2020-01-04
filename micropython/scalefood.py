import timer
import scale
#we want to keep this class independent of IO and display, so we can use it for simulations as well

class ScaleFood(scale.Scale):

    def __init__(self, display, cats, scale_cat):

        # scale configuration
        # super().__init__([7.619e-05])
        super().__init__([0.00219])
        self.calibrate_weight=10
        self.stable_auto_tarre_max=0.1
        self.stable_auto_tarre=600
        self.stable_measurements=2
        self.stable_skip_measurements=2
        self.stable_range=0.2 #production


        self.display=display
        self.cats=cats
        self.scale_cat=scale_cat

        #to calulate difference between measurements
        self.prev_weight=0

        #keep count when the cat isnt identified yet
        self.ate=0

        self.last_feed=0

        self.just_fed=True

        #retry a max number of times, after that we give an alert.
        self.feed_retries=0
        self.feed_max_retries=3

        try:
            self.load("scale_food.state")
            print("Loaded scale food")
            self.stable_reset()
        except Exception as e:
            print("Error loading scale food:"+str(e))

        #for now we always tarre the foodscale since it seems to get messed up sometimes
        self.tarre()


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

            #something bumped the food scale, so reset retry counter
            #(we dont react the actual event created by the feeder, since the current of the motor always creates an extra event.)
            self.feed_retries=0
            #NOTE: alerts are only used here for now, so its safe to reset every time
            self.display.alert(False)

            #ignore manually added food (>1g), or big jumps
            if diff<-1 or diff>2:
                #known cat, update its quota
                if self.cats.current_cat:

                    if self.ate:
                        self.cats.current_cat.ate(self.ate)
                        self.ate=0

                    self.cats.current_cat.ate(diff)

                    self.display.update_cat(self.cats.current_cat)


                else:
                    #unknown cat, store amount eaten temporary until we identify cat
                    if self.scale_cat.last_realtime_weight>100:
                        self.ate=self.ate+diff
                        self.display.msg("Unknown ate: {}g".format(self.ate))


        else:
            self.just_fed=False




        self.display.food_weight_stable(weight)



        # self.print_debug()

    def event_realtime(self, weight):
        """called on every measurement with actual value (non averaged)"""
        # print(weight)
        pass


    def event_unstable(self):
        """called once when scale leaves stable measurement"""

        self.display.food_weight_unstable()


    def msg(self, msg):
        self.display.msg("Food: "+msg)


    def should_feed(self):
        '''should we put food in the bowl?'''




        if self.state.calibrating:
            return False

        #wait between feeds, to prevent mayhem ;)
        if timer.diff(timer.timestamp,self.last_feed)>5000:
            #bowl is stable and empty?
            if self.stable and self.last_stable_weight<0.5:
                # all cats may have food, or current cat may have food?
                if self.cats.quota_all() or ( self.cats.current_cat and self.cats.current_cat.get_quota()>0):
                    self.last_feed=timer.timestamp
                    #if we have to retry too often, the feed silo is empty
                    self.feed_retries=self.feed_retries+1
                    if self.feed_retries<=self.feed_max_retries:
                        return True #feed
                    else:
                        #empty
                        self.display.msg("PLEASE REFILL!")
                        self.display.alert(True)

        return False #dont feed
