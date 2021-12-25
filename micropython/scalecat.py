import scale
import timer

#we want to keep this class independent of IO and display, so we can use it for simulations as well

class ScaleCat(scale.Scale):

    def __init__(self, display, cats, db):

        #configure scale
        super().__init__([0.00219]*4)
        self.calibrate_weight=200
        self.stable_auto_tarre_max=1000
        self.stable_auto_tarre=60000

        # self.stable_measurements=25
        # self.stable_skip_measurements=10
        # self.stable_range=50

        self.stable_measurements=10
        self.stable_skip_measurements=5
        self.stable_range=50

        self.display=display
        self.cats=cats
        self.db=db

        self.should_save=False


        #anti cheating: cat should leave scale first and cannot "morph" into another cat by sitting partially on the scale.
        self.cat_morph_timestamp=None

        try:
            self.load("scale_cat.state")
            print("Loaded scale cat")
            self.stable_reset()
        except Exception as e:
            print("Error loading scale cat:"+str(e))

        #always tarre cat scale on boot for now
        # self.tarre()



    #cat morphed, set cheat timeout
    def set_cat_morphed(self):

        self.display.msg("Cheating cat detected!")
        self.cat_morph_timestamp=timer.timestamp

    #check if the cheat timeout has been reached
    def is_cheating(self):

        #was there a cheat detected?
        if self.cat_morph_timestamp!=None:
            #still something on the scale, so restart timer
            if self.last_realtime_weight> self.cats.min_cat_weight:
                self.cat_morph_timestamp=timer.timestamp
            else:
                #scale has been empty for long enough?
                if timer.diff(timer.timestamp,self.cat_morph_timestamp)>60000*20:
                    self.display.msg("No longer cheating.")
                    self.cat_morph_timestamp=None
        return(self.cat_morph_timestamp!=None)


    def event_stable(self, weight):
        """called once after scale has been stable according to specified stable_ parameters"""

        #determine which cat it is
        cat=self.cats.by_weight(weight)

        #changed cat?
        if cat!=self.cats.current_cat:

            #suddenly changed from one cat to another one? probably cheating? (e.g. leaning off scale)
            if cat and self.cats.current_cat:
                self.set_cat_morphed()

            #store statistics of previous cat
            if self.cats.current_cat:
                #store this session and reset ate-counter
                self.db.store(self.cats.current_cat)
                    # #dont overwrite db errors on display
                    # self.display.msg("{} ate {:0.0f}g".format(self.cats.current_cat.state.name, self.cats.current_cat.ate_session), timeout=None)
                # self.cats.current_cat.ate_session=0
            if cat:
                #reset ate_session for new cat:
                cat.ate_session=0
            # else:
                #doing my part :)
                # self.display.msg("Subscribe2Pewdiepie!",10)



        self.cats.select_cat(cat)


        if cat:
            self.should_save=True


        if self.cats.current_cat:
            self.cats.current_cat.update_weight(weight)


        #display stuff
        self.display.scale_weight_stable(weight)
        self.display.update_cat(self.cats.current_cat)


        # self.print_debug()


    def event_realtime(self, weight):
        """called on every measurement with actual value (non averaged)"""
        self.display.scale_weight_realtime(weight)


    def event_unstable(self):
        """called once when scale leaves stable measurement"""


        self.display.scale_weight_unstable()
        pass

    def msg(self, msg):
        self.display.msg("Scale: "+msg)
