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

    def is_tarred(self):
        return self.__tarred

    def is_calibrated(self):
        return self.__calibrated

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
