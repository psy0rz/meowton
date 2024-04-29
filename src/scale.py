from asyncio import Event

from peewee import Model, CharField, FloatField, IntegerField

from db import db
from scale_sensor_calibration import ScaleSensorCalibration
from sensor_filter import SensorFilter


class Scale(Model):
    """scale class that does intput filtering, averaging and generates weigh-events"""

    ### settings that are stored in db
    name = CharField(primary_key=True)

    # percentage range which the scale should stay to be considered "stable"
    # biggest is used.
    stable_range = FloatField()
    stable_range_perc = FloatField()

    # for how many measurements should the scale be in the stable_range to be considered stable?
    stable_measurements = IntegerField()

    #NOTE: For the simple loadcells found on the meowton cat scale, the tarre drift can be as much as 100g by temperature fluctuations.
    # So auto tarre is essential for these! The more expensive loadcell in the foodcell does not drift, but autotarre is still usefull to
    # compensate for sticking debree and stuff.

    # Step size for self.calibration.auto_tarre()
    stable_auto_tarre_count = FloatField(default=0.1)

    # Auto tarre only under this weight.
    # 0 to disable
    stable_auto_tarre_max = FloatField(default=0)

    class Meta:
        database = db

    calibration: ScaleSensorCalibration
    sensor_filter: SensorFilter

    def __init__(self, *args, **kwargs):
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
        self.measure_spread_perc = 0

        # The system is always changing between stable and unstable.
        # A stable event will be followed by an unstable event and vice versa.
        self.event_stable = Event()
        self.event_unstable = Event()
        self.stable = False

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
            # WAS stable, so send unstable event
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

        # print(f"range {self.__measure_min}..{self.__measure_max}")
        self.measure_spread = (self.__measure_max - self.__measure_min)

        max_spread = max((self.stable_range_perc / 100 * weight), self.stable_range)

        # NOTE: only used in gui as feedback for user
        if max_spread > 0:
            self.measure_spread_perc = int(self.measure_spread * 100 / max_spread)
        else:
            self.measure_spread_perc = 0

        # reset if weight goes out of stable_range
        if self.measure_spread > max_spread:
            self.stable_reset(weight)
            return

        # do slow auto tarring when stable and below a certain weight
        if self.stable and abs(weight) < self.stable_auto_tarre_max:
            self.calibration.auto_tarre(raw_value, self.stable_auto_tarre_count)

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
                self.stable = True
                self.__event_stable()



db.create_tables([Scale])
