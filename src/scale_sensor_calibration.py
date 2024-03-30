# simple AX + B formula :)
class ScaleSensorCalibration:
    """Calibration and tarre offsets of a scale sensor. Should be stored persistant"""

    __offset: int
    __factor: float

    def __init__(self):
        self.__factor = 0
        self.__offset = 0

    def tarre(self, raw_value):
        self.__offset=raw_value

    def __tarred_value(self, raw_value):
        return raw_value-self.__offset

    def calibrate(self, raw_value, weight):
        tarred_value=self.__tarred_value(raw_value)
        self.__factor=weight/tarred_value

    def __calibrated_value(self, tarred_value):
        return tarred_value*self.__factor

    def weight(self, raw_value):
        tarred_value=self.__tarred_value(raw_value)
        return self.__calibrated_value(tarred_value)

    def print(self):
        print( f"offset={self.__offset}\tfactor={self.__factor}\t")


# TEST
if __name__=="__main__":

    raw_value=50

    calibration=ScaleSensorCalibration()
    calibration.tarre(raw_value)

    # increase of 20 is actual weight of 10g
    raw_value=raw_value+20
    calibration.calibrate(raw_value,10)

    print(calibration.weight(raw_value))     # 10g
    print(calibration.weight(raw_value+20))  # 20g

    calibration.print()
