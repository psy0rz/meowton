# simple AX + B formula :)
class ScaleSensorCalibration:
    """Calibration and tarre offsets of a scale sensor. Should be stored persistant"""

    offset: int
    factor: float

    def __init__(self):
        self.factor = 0
        self.offset = 0

    def tarre(self, raw_value:int):
        self.offset=raw_value

    def __tarred_value(self, raw_value):
        return raw_value-self.offset

    def calibrate(self, raw_value, weight):
        tarred_value=self.__tarred_value(raw_value)
        self.factor= weight / tarred_value

    def __calibrated_value(self, tarred_value) -> int:
        return int(tarred_value*self.factor)

    def weight(self, raw_value) -> int:
        tarred_value=self.__tarred_value(raw_value)
        return int(self.__calibrated_value(tarred_value))

    def print(self):
        print( f"offset={self.offset}\tfactor={self.factor}\t")


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
