import state
import linear_least_squares


"""
(weight)   |*
           | *
           |__*__________________________
           |  | **                       }
           |  |   ***                    } stable_range
           |  |      *****************   }
           |__|__________________________}
           |  |      |
           |  |      |
           |  |      |
           |  |      v
           |  |      stable_skip_measurements
              v
              (entered new stable range)

            ------------------------


    (measurement nr)



"""


class Scale:
    '''to calculate weights from raw data and do stuff like auto tarring and averaging

    Subclass this to actually do stuff (otherwise it will just print data)

    keeps state in self.state
    '''

    #subclass thesse event classes:

    def event_stable(self, timestamp, weight):
        """called once after scale has been stable according to specified stable_ parameters"""
        print("Stable averaged weight: {}g".format(weight))

    def event_realtime(self, timestamp, weight):
        """called on every measurement with actual value (non averaged)"""
        print("Weight: {}g".format(weight))

    def event_unstable(self, timestamp):
        """called once when scale leaves stable measurement"""
        print("Unstable")


    def __init__(self, calibrate_factors):

        self.state=state.State()




        # self.calibrate_weight=calibrate_weight
        self.calibrate_factors=calibrate_factors


        # range in grams in which the scale should stay to be considered "stable"
        self.stable_range=50

        # max timegap between two measurements (ms)
        self.stable_max_timegap=5000
        self.state.last_timestamp=0

        # for how many measurements should the scale be in the stable_range to be considered stable?
        self.stable_wait=25

        #number of measurements to skip when a new stable period is just entered. this is because the scale is still drifting
        self.stable_skip_measurements=10

        # number of measurements averaging after which to auto tarre
        self.stable_auto_tarre=100

        #max weight to tarre away (initial values will always be tarred)
        self.stable_auto_tarre_max=1500

        # #stable measurements and tarring only below this weight


        self.sensor_count=len(calibrate_factors)

        self.__stable_reset(0)


        #tarre offsets
        self.state.no_tarre=True
        self.state.offsets=[]
        for i in range(0, self.sensor_count):
            self.state.offsets.append(0)

        #last sensor readings
        self.state.current=[]

        self.state.calibrations=[]

    def __stable_reset(self, weight):
        self.state.stable_min=weight
        self.state.stable_max=weight
        self.state.stable_count=0
        self.state.stable_totals=[]
        self.state.stable_totals_count=0


        for i in range(0, self.sensor_count):
            self.state.stable_totals.append(0)


    def add_calibration(self,weight):
        '''add current raw measurement to calbration data, with specified weight. will automaticly recalibreate if there is enough data'''

        cal=self.offset(self.get_average())
        cal.append(weight)
        self.state.calibrations.append(cal)
        print("Added calibration {}".format(weight))

        # enough data?
        if (len(self.state.calibrations)>=self.sensor_count+1):
            #prepare matrix
            M = [ [0] * (self.sensor_count+1) for i in range(self.sensor_count) ]

            #add all measurements
            for cal in self.state.calibrations:
                for i in range(self.sensor_count):
                     linear_least_squares.vec_addsv( M[i], cal[i], cal )

            #do some more zmatt magic
            linear_least_squares.gaussian_elimination( M )

            self.calibrate_factors = [ M[i][4] for i in range(4) ]
            print("Recalibrated {}".format(self.calibrate_factors))



    def tarre(self):
        '''re-tarre scale as soon as possible (takes 10 measurements)'''
        self.__stable_reset(0)
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


    # def __stable_measurement(self,sensors):
        # '''determine if scale is stabilised and calculates average. '''



    def measurement(self, timestamp, sensors):
        """update measurent data and generate stable events when detected. timestamp in ms """

        self.state.current=sensors

        #calculate weight,
        weight=self.calibrated_weight(self.offset(sensors))

        self.event_realtime(timestamp, weight)

        # store stability statistics

        # reset stable measurement if there is a too big timegap
        if timestamp-self.state.last_timestamp>self.stable_max_timegap:
            self.__stable_reset(weight)
        self.state.last_timestamp=timestamp

        # keep min/max values
        if weight<self.state.stable_min:
            self.state.stable_min=weight

        if weight>self.state.stable_max:
            self.state.stable_max=weight

        # reset if weight goes out of stable_range
        if (self.state.stable_max - self.state.stable_min) <= self.stable_range:
            self.state.stable_count=self.state.stable_count+1
        else:
            #just became unstable?
            if self.state.stable_count>0:
                self.event_unstable(timestamp)
            self.__stable_reset(weight)

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
            (weight<=self.stable_auto_tarre_max and (self.state.stable_totals_count == self.stable_auto_tarre)) or
            (self.state.no_tarre and self.state.stable_totals_count == 10)
        ):
            # print("TARRE")
            self.state.offsets=self.get_average()
            self.state.no_tarre=False

        # generate measuring event, every stable_wait measurements
        if self.state.stable_totals_count>0 and self.state.stable_totals_count % self.stable_wait == 0:
            if self.state.stable_totals_count == self.stable_wait:
                self.event_stable(timestamp, self.calibrated_weight(self.offset(self.get_average())))




    def offset(self, sensors):
        '''return offsetted values of specified raw sensor values'''
        ret=[]
        sensor_nr=0
        for sensor in sensors:
            ret.append(sensor - self.state.offsets[sensor_nr])
            sensor_nr=sensor_nr+1
        return(ret)


    def calibrated_weight(self, sensors):
        '''return calibrated weight value of specified raw sensor values (dont forget to offset first)'''
        weight=0
        sensor_nr=0
        for sensor in sensors:
            weight=weight+sensor*self.calibrate_factors[sensor_nr]
            sensor_nr=sensor_nr+1

        return(weight)
