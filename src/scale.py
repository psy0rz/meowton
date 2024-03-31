from typing import Callable, TypeAlias

from scale_sensor_calibration import ScaleSensorCalibration

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


class Scale:
    """to calculate weights from raw data and do stuff like auto tarring and averaging"""

    calibration: ScaleSensorCalibration

    # subclass thesse event classes:
    def __init__(self, calibration: ScaleSensorCalibration, name: str, stable_range=50, stable_measurements=25,
                 stable_skip_measurements=10, stable_auto_tarre=200, stable_auto_tarre_max=0):

        self.calibration = calibration
        self.name = name

        self.__stable_subscriptions: [StableCallable] = []
        self.__unstable_subscriptions: [UnstableCallable] = []
        self.__realtime_subscriptions: [RealtimeCallable] = []

        # range in grams in which the scale should stay to be considered "stable"
        self.__stable_range = stable_range

        # for how many measurements should the scale be in the stable_range to be considered stable?
        self.__stable_measurements = stable_measurements

        # number of measurements to skip from measure_raw_sum when a new stable period is just entered. this is because the scale is still drifting
        self.__stable_skip_measurements = stable_skip_measurements

        # number of measurements averaging after which to auto tarre
        self.__stable_auto_tarre_count = stable_auto_tarre

        # max weight to tarre away (initial values will always be tarred)
        # 0 to disable
        self.__stable_auto_tarre_max = stable_auto_tarre_max

        # may also be used as API to get lastet weights/status:
        self.last_stable_weight = 0
        self.last_realtime_weight = 0
        self.last_realtime_raw_value = 0
        self.stable = False

        # actual measurement values for averaging and event generation:
        self.__measure_min = None
        self.__measure_max = None
        self.__measure_count = 0
        self.__measure_raw_sum = 0
        self.__measure_raw_sum_count = 0

    def __event_stable(self, weight: float):
        """called once after scale has been stable according to specified stable_ parameters"""
        print(f"{self.name}: Stable averaged weight: {weight:.0f}g")
        for cb in self.__stable_subscriptions:
            cb(weight)

    def __event_realtime(self, weight: float):
        """called on every measurement with actual value (non averaged)"""
        # print(f"{self.name}: Realtime: {weight:.2f}g (last stable {self.last_stable_weight:.2f})")
        for cb in self.__realtime_subscriptions:
            cb(weight)

    def __event_unstable(self):
        """called once when scale leaves stable measurement"""
        for cb in self.__unstable_subscriptions:
            cb()
        print("{self.name}: Unstable")

    def subscribe_stable(self, cb: StableCallable):
        self.__stable_subscriptions.append(cb)
        pass

    def subscribe_realtime(self, cb: RealtimeCallable):
        self.__realtime_subscriptions.append(cb)
        pass

    def subscribe_unstable(self, cb: UnstableCallable):
        self.__unstable_subscriptions.append(cb)
        pass

    def stable_reset(self):
        """resets stable state of the scale. (usefull after changing parameters of loading state)"""
        # print("RESET")
        self.__measure_min = None
        self.__measure_max = None
        self.__measure_count = 0
        self.__measure_raw_sum = 0
        self.__measure_raw_sum_count = 0
        self.stable = False


    def tarre(self):
        """tarre away current raw value"""
        self.calibration.tarre(self.last_realtime_raw_value)

    def calibrate(self, weight:int):
        """calibrate with specified weight. (dont forget to tarre first)"""
        self.calibration.calibrate(self.last_realtime_raw_value, weight)

    def measurement(self, raw_value:int):
        """update measurent data and generate stable events when detected. """

        # calculate weight,
        weight = self.calibration.weight(raw_value)

        self.last_realtime_weight = weight
        self.last_realtime_raw_value =raw_value
        self.__event_realtime(weight)

        # store stability statistics

        if self.__measure_min is None or weight < self.__measure_min:
            self.__measure_min = weight

        if self.__measure_max is None or weight > self.__measure_max:
            self.__measure_max = weight

        # reset if weight goes out of stable_range
        if (self.__measure_max - self.__measure_min) > self.__stable_range:
            self.stable_reset()
            return

        self.__measure_count = self.__measure_count + 1

        # do averaging or raw values, but skip the first measurements because of scale drifting and recovery
        if self.__measure_count >= self.__stable_skip_measurements:
            self.__measure_raw_sum = self.__measure_raw_sum + raw_value
            self.__measure_raw_sum_count = self.__measure_raw_sum_count + 1

        # do auto tarring:
        if self.__measure_count > self.__stable_auto_tarre_count and abs(weight) < self.__stable_auto_tarre_max:
            self.calibration.tarre(self.__measure_raw_sum / self.__measure_raw_sum_count)

        # generate stable measuring event
        if self.__measure_count == self.__stable_measurements:
            average_weight = self.calibration.weight(self.__measure_raw_sum / self.__measure_raw_sum_count)
            self.last_stable_weight = average_weight
            self.__event_stable(average_weight)
            self.stable = True
