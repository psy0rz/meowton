import timer
import scale
import time
import config
#we want to keep this class independent of IO and display, so we can use it for simulations as well

class ScaleFood(scale.Scale):

    def __init__(self, display, cats, scale_cat):

        # scale configuration
        # super().__init__([7.619e-05])
        super().__init__([0.00219])
        self.calibrate_weight=10
        self.stable_auto_tarre_max=0.1
        self.stable_auto_tarre=60000
        self.stable_measurements=2
        self.stable_skip_measurements=2
        self.stable_range=0.2 #production
        # self.stable_range=2 #test

        #assume food bowl is "empty" below this. (perhaps a few pieces of food left)
        self.empty_weight=0.5

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
        self.feed_max_retries=100

        self.last_feeding_hour=0

        try:
            self.load("scale_food.state")
            print("Loaded scale food")
            self.stable_reset()
        except Exception as e:
            print("Error loading scale food:"+str(e))

        #for now we always tarre the foodscale since it seems to get messed up sometimes
        # self.tarre()


    def fed(self):
        '''indicate we should ignore the current weight change'''
        self.stable_reset()
        self.just_fed=True

    def __event_stable(self, weight):
        """called once after scale has been stable according to specified stable_ parameters """


        diff=self.prev_weight-weight
        self.prev_weight=weight

        #if there is actual something in the bowl we can reset the retry counter.
        if weight>self.empty_weight*2:
            self.feed_retries=0

            (year, month, mday, hour, minute, second, weekday, yearday) = time.localtime()
            self.last_feeding_hour=hour

        #ignore weight change after despensing food
        if not self.just_fed:

            #NOTE: alerts are only used here for now, so its safe to reset every time
            self.display.alert(False)

            #If more than this is added to the scale, its probably cheating or falling from the feeder somehow and not added to cats quota. 
            #Otherwise we assume food felt back from the cats mouth into the scale, so its added back to the cats quota. (since he didnt eat it)
            cheat_threshold=0.5 

            #Assume the cat can not remove more than this in one time, so dont substract from quota.
            #This can happen when the bowl is removed. (When its added it usually more than the cheat threshold so its ignored again)
            remove_threshold=4

            #>0 means food was lost from scale
            #<0 means food was added to scale
            if diff>-cheat_threshold and diff<remove_threshold:  
                #known cat, update its quota
                if self.cats.current_cat:

                    if self.ate:
                        self.cats.current_cat.ate(self.ate)
                        self.ate=0

                    self.cats.current_cat.ate(diff)

                    self.display.update_cat(self.cats.current_cat)


                else:
                    #unknown cat, store amount eaten temporary until we identify cat
                    # if self.scale_cat.last_realtime_weight>100:
                    self.ate=self.ate+diff
            else:
                self.display.msg("Ignored food change: {:2.2f}g".format(diff))


        else:
            self.just_fed=False




        self.display.food_weight_stable(weight)



        # self.print_debug()

    def __event_realtime(self, weight):
        """called on every measurement with actual value (non averaged)"""
        # print("food = {:.2f}g".format(weight))
        pass


    def __event_unstable(self):
        """called once when scale leaves stable measurement"""

        self.display.food_weight_unstable()


    def msg(self, msg):
        self.display.msg("Food: "+msg)


    def should_feed(self):
        '''should we put food in the bowl?'''


        if self.calibration.calibrating:
            return False

        #cheating
        if self.scale_cat.is_cheating():
            return False

        (year, month, mday, hour, minute, second, weekday, yearday) = time.localtime()


        #wait between feeds, to prevent mayhem ;)
        if timer.diff(timer.timestamp,self.last_feed)>5000:
            #bowl is stable and empty and not removed (<-5) and cat scale is also not removed (>-100)?
            if self.stable and self.last_stable_weight<self.empty_weight and self.last_stable_weight>-5 and self.scale_cat.last_stable_weight>-100:
                # all cats may have food, or current cat may have food or its feeding time?
                if self.cats.quota_all() or ( self.cats.current_cat and self.cats.current_cat.get_quota()>0) or (self.last_feeding_hour!=hour and hour in config.feed_times):
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
