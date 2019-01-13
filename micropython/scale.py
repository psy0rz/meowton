from lib.state import State
import linear_least_squares
import timer

"""
(weight)    *
             *
            __*__________________________
              | **                       }
              |   ***                    } stable_range
              |      *########********   }
            __|__________________________}
              |       |      |
              |       |<---->|<EVENT
              |       |   stable_measurements
              |<----->|
              |   stable_skip_measurements
              v
              (entered new stable range)


                   (measurement nr)

"""


class Scale(State):
    '''to calculate weights from raw data and do stuff like auto tarring and averaging

    Subclass this to actually do stuff (otherwise it will just print data)

    keeps state in self.state
    '''

    #subclass thesse event classes:

    def event_stable(self, weight):
        """called once after scale has been stable according to specified stable_ parameters"""
        print("Stable averaged weight: {}g".format(weight))
        self.debug()

    def event_realtime(self, weight):
        """called on every measurement with actual value (non averaged)"""
        print("Weight: {}g".format(weight))

    def event_unstable(self):
        """called once when scale leaves stable measurement"""
        print("Unstable")


    def __init__(self, default_factors):

        super().__init__()

        ### configure all these parameters in your subclass!

        # weight to use during calibration
        self.calibrate_weight=100

        # range in grams in which the scale should stay to be considered "stable"
        self.stable_range=50

        # max timegap between two measurements (ms)
        self.stable_max_timegap=5000

        # for how many measurements should the scale be in the stable_range to be considered stable?
        self.stable_measurements=25

        #number of measurements to skip when a new stable period is just entered. this is because the scale is still drifting
        self.stable_skip_measurements=10

        # number of measurements averaging after which to auto tarre
        self.stable_auto_tarre=100

        #max weight to tarre away (initial values will always be tarred)
        self.stable_auto_tarre_max=1500


        ### internal states, do not configure these.
        # everything in self.state can be saved and reloaded upon restart

        #calibration default factors. number of factors decides the number of sensors
        # self.__default_factors=default_factors
        self.sensor_count=len(default_factors)
        # self.state.calibrate_factors=default_factors.copy()
        self.recalibrate()

        self.state.last_timestamp=0


        #may also be used as API to get lastet weights/status:
        self.last_stable_weight=0
        self.last_realtime_weight=0
        self.stable=False

        self.stable_reset(0)

        #tarre offsets
        self.state.no_tarre=True
        self.state.offsets=[]
        for i in range(0, self.sensor_count):
            self.state.offsets.append(0)

        #last sensor readings
        self.state.current=[]

        #calibration measurements (you can add more on the fly)
        # self.state.calibrations=[]



    def stable_reset(self, weight=None):
        """resets stable state of the scale. (usefull after changing parameters of loading state)"""
        # print("RESET")
        self.state.stable_min=weight
        self.state.stable_max=weight
        self.state.stable_count=0
        self.state.stable_totals=[]
        self.state.stable_totals_count=0
        self.debug=[]

        if self.stable:
            self.event_unstable()

        self.stable=False


        for i in range(0, self.sensor_count):
            self.state.stable_totals.append(0)


    # Disabled for now, it works but its more inaccurate compared to normale calibration
    # def add_calibration(self,weight):
    #     '''add current raw measurement to calbration data, with specified weight. will automaticly recalibreate if there is enough data'''
    #
    #     cal=self.offset(self.get_average())
    #     cal.append(weight)
    #     self.state.calibrations.append(cal)
    #     print("Added calibration {}".format(weight))
    #
    #     # enough data?
    #     if (len(self.state.calibrations)>=self.sensor_count):
    #         #prepare matrix
    #         M = [ [0] * (self.sensor_count+1) for i in range(self.sensor_count) ]
    #
    #         #add all measurements
    #         for cal in self.state.calibrations:
    #             for i in range(self.sensor_count):
    #                  linear_least_squares.vec_addsv( M[i], cal[i], cal )
    #
    #         #do some more zmatt magic
    #         linear_least_squares.gaussian_elimination( M )
    #
    #         self.state.calibrate_factors = [ M[i][self.sensor_count] for i in range(self.sensor_count) ]
    #         # print("Recalibrated {}".format(self.state.calibrate_factors))

    def recalibrate(self):
        '''reset calibration to factory default and start recalibration procedure'''

        # Rcalibration should allow for widely different and mixed sensors in one system
        # It will first measure noise levels and then try to calibrate

        self.state.calibrating=True
        self.cal_states=[]
        self.cal_count=0
        self.state.calibrate_factors=[None]*self.sensor_count

    def __calibrate(self, sensors):
        '''do calibration magic'''

        if not self.state.calibrating:
            return False

        self.cal_count=self.cal_count+1

        ### Step 1: just started, init with current sensor values
        if not self.cal_states:
            self.msg("Calibrating...")
            for sensor in sensors:
                self.cal_states.append({
                    'min': sensor,
                    'max': sensor,
                    'start_avg': None,
                    'noise': None,
                    'avg': sensor,
                })
        else:
            # keep track of averages and min/max range, per sensor
            for i in range(0,self.sensor_count):

                self.cal_states[i]['avg']*0.9+sensors[i]*0.1

                if sensors[i]<self.cal_states[i]['min']:
                    self.cal_states[i]['min']=sensors[i]

                if sensors[i]>self.cal_states[i]['max']:
                    self.cal_states[i]['max']=sensors[i]

            ### Step 2: determining noise range and start average:
            if self.cal_states[0]['start_avg']==None:

                # wait until we have 10 measurements:
                if self.cal_count==30:
                    #done, store start_average and noise, continue to next step
                    for cal_state in self.cal_states:
                        cal_state['start_avg']=cal_state['avg']
                        cal_state['noise']=abs(cal_state['max']-cal_state['min'])
                    self.cal_count==0
                    self.msg("Place cal. {:2.0f}g".format(self.calibrate_weight))

            else:
                ### Step 3: detect calibration weight:

                for i in range(0,self.sensor_count):
                    # big change of 10x noise?
                    if abs(self.cal_states[i]['avg']-sensors[i])>self.cal_states[i]['noise']*10:
                        # reset average and count
                        self.cal_states[i]['avg']=sensors[i]
                        self.cal_count=0

                if self.cal_count==0:
                    self.msg("Place cal. weight")

                # stable for a while?
                if self.cal_count==30:
                    for i in range(0,self.sensor_count):
                        # all averages that are still >10x compared to start average can be calibrated now:
                        diff=self.cal_states[i]['avg']-self.cal_states[i]['start_avg']
                        if abs(diff)>self.cal_states[i]['noise']*10:
                            self.state.calibrate_factors[i]=self.calibrate_weight/diff
                            self.msg("Calibrated {}".format(i))

                    # done?
                    if not None in self.state.calibrate_factors:
                        self.state.calibrating=False
                        self.cal_states=None
                        self.msg("Calbration done")


        return True





        # averages=self.offset(self.get_average())
        # weights=self.calibrated_weights(averages)
        # zeros=0
        # factor=0
        # for sensor in range(0,self.sensor_count):
        #     if abs(weights[sensor]-self.calibrate_weight)<self.calibrate_weight*0.5: #the calibrating sensor should be least 50% in range
        #         factor=self.calibrate_weight/averages[sensor]
        #         cal_sensor=sensor
        #     if abs(weights[sensor])<=self.calibrate_weight*0.01: # others should be not more than 1% of zero
        #         zeros=zeros+1
        #
        # #the calibration weight is placed on exactly one sensor?
        # if zeros==self.sensor_count-1 and factor:
        #     self.state.calibrate_factors[cal_sensor]=factor
        #
        #     #done?
        #     for sensor in range(0,self.sensor_count):
        #         #Note: there is no way a cell calibrates exactly on this factor :)
        #         if self.state.calibrate_factors[sensor]==self.__default_factors[sensor]:
        #             self.msg("ok next")
        #             return
        #
        #     self.state.calibrating=False
        #     self.msg("Cal. done")
        #     self.save()
        # else:
        #
        #     self.msg("place {}g ".format(self.calibrate_weight))




    def tarre(self):
        '''re-tarre scale as soon as possible (takes 10 measurements)'''
        self.stable_reset(0)
        self.state.no_tarre=True

    def get_average(self):
        '''gets raw average values since of this stable period'''
        ret=[]
        for total in self.state.stable_totals:
            ret.append(int(total/self.state.stable_totals_count))
        return(ret)

    def get_current(self):
        return(self.state.current)

    def get_average_count(self):
        '''number of samples the current average is caculated over'''
        return(self.state.stable_totals_count)





    def measurement(self, sensors):
        """update measurent data and generate stable events when detected. """

        if self.__calibrate(sensors):
            return


        self.state.current=sensors

        #calculate weight,
        weight=self.calibrated_weight(self.offset(sensors))

        self.last_realtime_weight=weight
        self.event_realtime(weight)


        # store stability statistics

        # reset stable measurement if there is a too big timegap
        if timer.diff(timer.timestamp,self.state.last_timestamp)>self.stable_max_timegap:
            self.stable_reset(weight)
        self.state.last_timestamp=timer.timestamp

        # keep min/max values
        if self.state.stable_min==None or weight<self.state.stable_min:
            self.state.stable_min=weight

        if self.state.stable_max==None or weight>self.state.stable_max:
            self.state.stable_max=weight

        # reset if weight goes out of stable_range
        if (self.state.stable_max - self.state.stable_min) <= self.stable_range:
            self.state.stable_count=self.state.stable_count+1
        else:
            # print("RESET: range")
            self.stable_reset(weight)

        #debug: store the measurements that happend between unstable and stable
        if self.state.stable_totals_count <= self.stable_measurements:
            self.debug.append(weight)

        # do averaging, but skip the first measurements because of scale drifting and recovery
        # note that we average the raw data for better accuracy
        if self.state.stable_count>=self.stable_skip_measurements:
            sensor_nr=0
            for sensor in sensors:
                self.state.stable_totals[sensor_nr]=self.state.stable_totals[sensor_nr]+sensor
                sensor_nr=sensor_nr+1

            self.state.stable_totals_count=self.state.stable_totals_count+1

        # do auto tarring:
        # only under a certain weight and for a long stability period, or if its the first time do it quickly to get started
        if (
            (abs(weight)<=self.stable_auto_tarre_max and (self.state.stable_totals_count == self.stable_auto_tarre)) or
            (self.state.no_tarre and self.state.stable_totals_count == 10)
        ):
            # print("TARRE")
            self.state.offsets=self.get_average()
            self.state.no_tarre=False

        # generate measuring event
        if self.state.stable_totals_count == self.stable_measurements and not self.state.no_tarre:
            average_weight=self.calibrated_weight(self.offset(self.get_average()))
            self.debug.append(average_weight)
            self.last_stable_weight=average_weight
            self.event_stable(average_weight)
            self.stable=True




    def offset(self, sensors):
        '''return offsetted values of specified raw sensor values'''
        ret=[]
        sensor_nr=0
        for sensor in sensors:
            ret.append(sensor - self.state.offsets[sensor_nr])
            sensor_nr=sensor_nr+1
        return(ret)


    def calibrated_weights(self, sensors):
        '''return calibrated weight values of specified raw sensor values (dont forget to offset first)'''
        weights=[]
        sensor_nr=0
        for sensor in sensors:
            weights.append(sensor*self.state.calibrate_factors[sensor_nr])
            sensor_nr=sensor_nr+1

        return(weights)


    def calibrated_weight(self, sensors):
        '''return total calibrated weight value of specified raw sensor values (dont forget to offset first)'''
        weights=self.calibrated_weights(sensors)
        total=0
        for weight in weights:
            total=total+weight

        return(total)

    def print_debug(self):
        weight=self.debug.pop()
        s="Measured {:0.2f}g: ".format(weight)
        for m in self.debug:
            s=s+"{:0.2f}g ".format(m-weight)
        print(s)


    def msg(self, msg):
        '''display message for user (overwrite in subclass)'''
        print("Scale: "+msg)
