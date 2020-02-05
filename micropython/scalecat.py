import scale

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

        try:
            self.load("scale_cat.state")
            print("Loaded scale cat")
            self.stable_reset()
        except Exception as e:
            print("Error loading scale cat:"+str(e))

        #always tarre cat scale on boot for now
        self.tarre()





    def event_stable(self, weight):
        """called once after scale has been stable according to specified stable_ parameters"""

        #determine which cat it is
        cat=self.cats.by_weight(weight)

        #changed cat?
        if cat!=self.cats.current_cat:
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
        # print(weight)
        pass


    def event_unstable(self):
        """called once when scale leaves stable measurement"""


        self.display.scale_weight_unstable()
        pass

    def msg(self, msg):
        self.display.msg("Scale: "+msg)
