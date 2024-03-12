from time import time
from typing import Callable, TypeAlias

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

StableCallable: TypeAlias = Callable[[float], None]
RealtimeCallable: TypeAlias = Callable[[float], None]
UnstableCallable: TypeAlias = Callable[[], None]


class ScaleCalibration:
    """Calibration and tarre offsets of the scale. Should be stored persistant"""

    __offsets: list[int]
    __tarred: bool  # true when offsets are valid (scale is tarred)

    __factors: list[float]
    __calibrated: bool  # true when factors are valid


    def __init__(self, sensor_count: int):
        self.__factors = [0] * sensor_count
        self.__calibrated = False

        self.__tarred = False
        self.__offsets = [0] * sensor_count


    def is_valid(self):
        return self.__calibrated and self.__tarred

    def untarre(self):
        self.__tarred=False

    def tarre(self, raw_sensors):
        '''store sensor values as tarre value'''
        self.__offsets=raw_sensors
        self.__tarred = True

    def uncalibrate(self):
        self.__calibrated=False

    def calibrate(self, raw_sensors, weight):
        '''calibrate scale with raw sensor values, assuming weight was placed on them.'''
        offsetted=self.__tarred_sensors(raw_sensors)

        sensor_nr = 0
        self.__factors=[]
        for sensor in offsetted:
            weights.append(sensor * self.__factors[sensor_nr])
            sensor_nr = sensor_nr + 1

        self.__calibrated=True


    def __tarred_sensors(self, raw_sensors):
        '''return offsetted values of specified raw sensor values (applies tarre)'''
        ret = []
        sensor_nr = 0
        for sensor in raw_sensors:
            ret.append(sensor - self.__offsets[sensor_nr])
            sensor_nr = sensor_nr + 1
        return (ret)

    def __calibrated_sensors(self, offsetted_sensors):
        '''return calibrated weight values of specified raw sensor values (dont forget to offset first)'''

        if not self.__calibrated:
            return ([0] * len(self.__factors))

        weights = []
        sensor_nr = 0
        for sensor in offsetted_sensors:
            weights.append(sensor * self.__factors[sensor_nr])
            sensor_nr = sensor_nr + 1

        return (weights)

    def weight(self, raw_sensors):
        '''return total calibrated weight value of specified raw sensor values '''
        offsetted=self.__tarred_sensors(raw_sensors)
        calibrated=self.__calibrated_sensors(offsetted)

        total = 0
        for weight in calibrated:
            total = total + weight

        return (total)




class SensorState:
    """used during calibration"""

    MOVING_AVG_FACTOR=0.1

    def __init__(self, value):
        self.min = value
        self.max = value
        self.start_avg = 0
        self.noise = 0
        self.moving_avg = value


    def measure(self, value):

        self.moving_avg = self.moving_avg * ( 1-self.MOVING_AVG_FACTOR) * (value*self.MOVING_AVG_FACTOR)

        if value < self.min:
            self.min=value

        if value > self.max:
            self.max=value


        ### Step 1: determining noise range and start average:
        if self.cal_states[0]['start_avg'] == None:
            # wait until we have enough measurements:
            cal_count_needed = 50
            self.msg("Measuring noise ({}%)".format(int(self.cal_count * 100 / cal_count_needed)))
            if self.cal_count == cal_count_needed:
                # done, store start_average and noise, continue to next step
                for cal_state in self.cal_states:
                    cal_state['start_avg'] = cal_state['avg']
                    cal_state['noise'] = abs(cal_state['max'] - cal_state['min']) * 2  # add huge margin
                self.cal_count = 0

        else:
            ### Step 2: detect calibration weights:
            cal_count_needed = 30

            # restart averaging when there is a big change on a sensor
            for i in range(0, self.sensor_count):
                if abs(self.cal_states[i]['avg'] - sensors[i]) > self.cal_states[i]['noise']:
                    self.cal_count = 0
                    self.cal_states[i]['avg'] = sensors[i]  # start averaging from here on
                    # self.msg("sensor {}, noise {}, avg {}, current {}".format(i, self.cal_states[i]['noise'], self.cal_states[i]['avg'], sensors[i]))

            # i=0
            # self.msg("sensor {}, noise {}, avg {}, current {}".format(i, self.cal_states[i]['noise'], self.cal_states[i]['avg'], sensors[i]))

            # there is something on a sensor?
            for i in range(0, self.sensor_count):
                if abs(self.cal_states[i]['start_avg'] - sensors[i]) > self.cal_states[i]['noise']:
                    # calibrating..
                    if self.cal_count < cal_count_needed:
                        self.msg(
                            "Calibrating sensor {} ({}%)".format(i, int(self.cal_count * 100 / cal_count_needed)))
                    # done...
                    if self.cal_count == cal_count_needed:
                        # this sensor is done now:
                        diff = self.cal_states[i]['avg'] - self.cal_states[i]['start_avg']
                        self.calibration.__factors[i] = self.calibrate_weight / diff
                    # please remove..
                    if self.cal_count > cal_count_needed:
                        self.msg("Remove weight from sensor {}".format(i))

                    return True

            # there is nothing on a sensor?
            self.msg("Place {}g on next sensor.".format(self.calibrate_weight))

            if not None in self.calibration.__factors:
                self.calibration.calibrating = False
                self.cal_states = None
                self.tarre()
                self.msg("Calbration done")
                print(self.calibration.__factors)


class Scale:
    """to calculate weights from raw data and do stuff like auto tarring and averaging"""

    calibration: ScaleCalibration

    # subclass thesse event classes:
    def __init__(self, sensor_count):

        self.calibration = ScaleCalibration(sensor_count)
        self.__stable_subscriptions: [StableCallable] = []
        self.__unstable_subscriptions: [UnstableCallable] = []
        self.__realtime_subscriptions: [RealtimeCallable] = []

        ### configure all these parameters in your subclass!

        # weight to use during calibration
        self.calibrate_weight = 200

        # range in grams in which the scale should stay to be considered "stable"
        self.stable_range = 50

        # max timegap between two measurements
        self.stable_max_timegap = 5

        # for how many measurements should the scale be in the stable_range to be considered stable?
        self.stable_measurements = 25

        # number of measurements to skip when a new stable period is just entered. this is because the scale is still drifting
        self.stable_skip_measurements = 10

        # number of measurements averaging after which to auto tarre
        self.stable_auto_tarre = 200

        # max weight to tarre away (initial values will always be tarred)
        self.stable_auto_tarre_max = 1500

        ### internal states, do not configure these.
        # everything in self.state can be saved and reloaded upon restart

        self.sensor_count = sensor_count

        # self.cal_states=[]
        # self.cal_count=0

        # may also be used as API to get lastet weights/status:
        self.last_stable_weight = 0
        self.last_realtime_weight = 0
        self.stable = False

        self.stable_reset(0)

        if not self.is_calibrated():
            self.msg("Scale need to be calibrated.")

    def __event_stable(self, weight: float):
        """called once after scale has been stable according to specified stable_ parameters"""
        print(f"Stable averaged weight: {weight:.0f}g")
        for cb in self.__stable_subscriptions:
            cb(weight)

    def __event_realtime(self, weight: float):
        """called on every measurement with actual value (non averaged)"""
        print(f"Realtime: {weight:.2f}g (last stable {self.last_stable_weight:.2f})")
        for cb in self.__realtime_subscriptions:
            cb(weight)

    def __event_unstable(self):
        """called once when scale leaves stable measurement"""
        for cb in self.__unstable_subscriptions:
            cb()
        print("Unstable")

    def subscribe_stable(self, cb: StableCallable):
        self.__stable_subscriptions.append(cb)
        pass

    def subscribe_realtime(self, cb: RealtimeCallable):
        self.__realtime_subscriptions.append(cb)
        pass

    def subscribe_unstable(self, cb: UnstableCallable):
        self.__unstable_subscriptions.append(cb)
        pass

    def is_calibrated(self):
        return self.calibration.__calibrated

    def stable_reset(self, weight=None):
        """resets stable state of the scale. (usefull after changing parameters of loading state)"""
        # print("RESET")
        self.stable_min = weight
        self.stable_max = weight
        self.stable_count = 0
        self.stable_totals = []
        self.stable_totals_count = 0
        # self.debug = []

        if self.stable:
            self.__event_unstable()

        self.stable = False

        for i in range(0, self.sensor_count):
            self.stable_totals.append(0)

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
        """start calibration procedure"""

        # Rcalibration should allow for widely different and mixed sensors in one system
        # It will first measure noise levels and then try to calibrate

        self.calibrating = True
        self.cal_states = []
        self.cal_count = 0

    def __calibrate(self, sensors):
        '''do calibration magic'''

        if not self.calibrating:
            return False

        self.cal_count = self.cal_count + 1
        # self.msg(str(self.cal_count));

        # just started, init with current sensor values
        if not self.cal_states:
            for sensor in sensors:
                self.cal_states.append(SensorState(sensor))
        else:

            # keep track of averages and min/max range, per sensor
                for i in range(0, self.sensor_count):
                    self.sensor_states[i].measure(sensors[i])


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
        self.msg("Tarring...")
        self.stable_reset(0)
        self.calibration.untarre()

    def get_raw_average(self):
        '''gets raw average values since of this stable period'''
        ret = []
        for total in self.stable_totals:
            ret.append(int(total / self.stable_totals_count))
        return (ret)

    def get_average_count(self):
        '''number of samples the current average is caculated over'''
        return (self.stable_totals_count)

    def measurement(self, sensors):
        """update measurent data and generate stable events when detected. """

        if self.__calibrate(sensors):
            return

        # calculate weight,
        weight = self.calibrated_weight(self.offset(sensors))

        self.last_realtime_weight = weight
        self.__event_realtime(weight)

        # store stability statistics

        # reset stable measurement if there is a too big timegap
        if time() - self.calibration.last_timestamp > self.stable_max_timegap:
            self.stable_reset(weight)
        self.calibration.last_timestamp = time()

        # keep min/max values
        if self.calibration.stable_min == None or weight < self.calibration.stable_min:
            self.calibration.stable_min = weight

        if self.calibration.stable_max == None or weight > self.calibration.stable_max:
            self.calibration.stable_max = weight

        # reset if weight goes out of stable_range
        if (self.calibration.stable_max - self.calibration.stable_min) <= self.stable_range:
            self.calibration.stable_count = self.calibration.stable_count + 1
        else:
            # print("RESET: range")
            self.stable_reset(weight)

        # debug: store the measurements that happend between unstable and stable
        # if self.state.stable_totals_count <= self.stable_measurements:
        #     self.debug.append(weight)

        # do averaging, but skip the first measurements because of scale drifting and recovery
        # note that we average the raw data for better accuracy
        if self.stable_count >= self.stable_skip_measurements:
            sensor_nr = 0
            for sensor in sensors:
                self.stable_totals[sensor_nr] = self.stable_totals[sensor_nr] + sensor
                sensor_nr = sensor_nr + 1

            self.stable_totals_count = self.stable_totals_count + 1

        # do auto tarring:
        # only under a certain weight and for a long stability period, or if its the first time do it quickly to get started
        if (
                # (abs(weight)<=self.stable_auto_tarre_max and (self.state.stable_totals_count == self.stable_auto_tarre)) or
                (weight <= self.stable_auto_tarre_max and (self.stable_totals_count == self.stable_auto_tarre)) or
                (not self.calibration.__tarred and self.stable_totals_count == 10)
        ):
            # print("TARRE")
            self.msg("Tarred.")
            self.calibration.__offsets = self.get_raw_average()
            self.calibration.__tarred = True
            self.stable_reset()

        # generate measuring event
        if self.stable_totals_count == self.stable_measurements and self.calibration.__tarred:
            average_weight = self.calibrated_weight(self.offset(self.get_raw_average()))
            # self.debug.append(average_weight)
            self.last_stable_weight = average_weight
            self.__event_stable(average_weight)
            self.stable = True



    # def print_debug(self):
    #     weight = self.debug.pop()
    #     s = "Measured {:0.2f}g: ".format(weight)
    #     for m in self.debug:
    #         s = s + "{:0.2f}g ".format(m - weight)
    #     print(s)

    def msg(self, msg):
        '''display message for user (overwrite in subclass)'''
        print("Scale: " + msg)
