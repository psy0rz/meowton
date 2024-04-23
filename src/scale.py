from asyncio import Event

from peewee import Model, CharField, FloatField, IntegerField

from db import db
from scale_sensor_calibration import ScaleSensorCalibration
from sensor_filter import SensorFilter

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



class Scale(Model):
    """scale class that does intput filtering, averaging and generates weigh-events"""

    ### settings that are stored in db
    name = CharField(primary_key=True)

    # range in grams in which the scale should stay to be considered "stable"
    stable_range = FloatField()

    # for how many measurements should the scale be in the stable_range to be considered stable?
    stable_measurements = IntegerField()

    # number of measurements averaging after which to auto tarre
    stable_auto_tarre_count = IntegerField(default=600)

    # max weight to tarre away (initial values will always be tarred)
    # 0 to disable
    stable_auto_tarre_max = IntegerField(default=0)

    class Meta:
        database = db

    calibration: ScaleSensorCalibration
    sensor_filter: SensorFilter

    def __init__(self, *args, **kwargs):
        """
        Initializes an instance of the class.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None

        Attributes:
            sensor_filter (SensorFilter): The sensor filter associated with the instance.
            calibration (ScaleSensorCalibration): The calibration associated with the instance.
            last_stable_weight (float): The last stable weight recorded by the instance.
            last_realtime_weight (float): The last real-time weight recorded by the instance.
            last_realtime_raw_value (float): The last real-time raw value recorded by the instance.
            __measure_min (float): The minimum measurement value used for averaging and event generation.
            __measure_max (float): The maximum measurement value used for averaging and event generation.
            __measure_count (int): The count of measurements used for averaging and event generation.
            __measure_raw_sum (float): The sum of raw measurements used for averaging and event generation.
            __measure_raw_sum_count (int): The count of raw measurements used for averaging and event generation.
            measure_countdown (int): The count down to stabilization.
            measure_spread (int): The spread of measurements.
            stable_event (Event): An event triggered when the measurement stabilizes.
            unstable_event (Event): An event triggered when the measurement becomes unstable.
        """
        super().__init__(*args, **kwargs)
        self.sensor_filter = SensorFilter.get_or_create(name=self.name)[0]
        self.calibration = ScaleSensorCalibration.get_or_create(name=self.name)[0]


        # may also be used as API to get lastet weights/status:
        self.last_stable_weight = 0
        self.last_realtime_weight = 0
        self.last_realtime_raw_value = 0

        # actual measurement values for averaging and event generation:
        self.__measure_min = None
        self.__measure_max = None
        self.__measure_count = 0
        self.__measure_raw_sum = 0
        self.__measure_raw_sum_count = 0

        # counts down to zero while stabilizing
        self.measure_countdown = 0
        self.measure_spread = 0


        # The system is always changing between stable and unstable.
        # A stable event will be followed by an unstable event and vice versa.
        self.event_stable=Event()
        self.event_unstable=Event()
        self.stable=False

        self.stable_reset()

    def __event_stable(self):
        """called once after scale has been stable according to specified stable_ parameters"""
        print(f"Scale [{self.name}]: Stable: {self.last_stable_weight:0.2f}g")
        self.event_stable.set()
        self.event_stable.clear()

    # def __event_realtime(self, weight: float):
    #     """called on every measurement with actual value (non averaged)"""
    #     # print(f"{self.name}: Realtime: {weight:.2f}g (last stable {self.last_stable_weight:.2f})")
    #     for cb in self.__realtime_subscriptions:
    #         cb(weight)

    def __event_unstable(self):
        """called once when scale leaves stable measurement"""
        print(f"Scale [{self.name}]: Unstable")
        self.event_unstable.set()
        self.event_unstable.clear()


    def tarre(self):
        """tarre away current raw value"""
        self.calibration.tarre(self.last_realtime_raw_value)

    def calibrate(self, weight: int):
        """calibrate with specified weight. (dont forget to tarre first)"""
        self.calibration.calibrate(self.last_realtime_raw_value, weight)

    def stable_reset(self, weight=None):
        """resets stable state of the scale. (usefull after changing parameters of loading state)"""
        # print("RESET")
        self.__measure_min = weight
        self.__measure_max = weight
        self.__measure_raw_sum = 0
        self.__measure_raw_sum_count = 0
        if self.stable:
            #WAS stable, so send unstable event
            self.stable = False
            self.__event_unstable()

        self.measure_countdown = self.stable_measurements

    def measurement(self, raw_value: int):
        """update measurent data and generate stable events when detected. """

        # sensor filtering
        if not self.sensor_filter.valid(raw_value):
            return

        # calculate weight,
        weight = self.calibration.weight(raw_value)

        self.last_realtime_weight = weight
        self.last_realtime_raw_value = raw_value

        # store stability statistics
        if self.__measure_min is None or weight < self.__measure_min:
            self.__measure_min = weight

        if self.__measure_max is None or weight > self.__measure_max:
            self.__measure_max = weight

        self.measure_spread = abs(self.__measure_max - self.__measure_min)

        # reset if weight goes out of stable_range
        if (self.__measure_max - self.__measure_min) > self.stable_range:
            self.stable_reset(weight)
            return

        # do averaging or raw values, but skip the first measurements because of scale drifting and recovery
        # if self.__measure_count >= self.__stable_skip_measurements:
        self.__measure_raw_sum = self.__measure_raw_sum + raw_value
        self.__measure_raw_sum_count = self.__measure_raw_sum_count + 1

        # generate stable measuring event
        if self.measure_countdown > 0:
            self.measure_countdown = self.measure_countdown - 1
            if self.measure_countdown == 0:
                average_weight = self.calibration.weight(self.__measure_raw_sum / self.__measure_raw_sum_count)
                self.last_stable_weight = average_weight
                self.stable=True
                self.__event_stable()

        # do auto tarring:
        if self.__measure_raw_sum_count > self.stable_auto_tarre_count and abs(weight) < self.stable_auto_tarre_max:
            self.calibration.tarre(int(self.__measure_raw_sum / self.__measure_raw_sum_count))


db.create_tables([Scale])
