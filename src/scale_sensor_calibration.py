# simple AX + B formula :)
import time

from peewee import Model, CharField, FloatField, IntegerField

from db import db


class ScaleSensorCalibration(Model):
    """Calibration and tarre offsets of a scale sensor."""

    name = CharField(primary_key=True)
    offset = IntegerField(default=0)
    factor = FloatField(default=0)

    class Meta:
        database = db

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.last_save_time=time.time()

    def tarre(self, raw_value: int):
        self.offset = raw_value

    def auto_tarre(self, raw_value: int, step_size: float):
        """slowly auto-tarre the raw value away. increases or decreases offset with step_size every time"""
        if raw_value > self.offset:
            self.offset += step_size
        elif raw_value < self.offset:
            self.offset -= step_size

        #save every hour, to survive restarts (since auto tarring takes long)
        if time.time()-self.last_save_time > 3600:
            print(f"{self.__class__}: Saving auto tarre value.")
            self.save()
            self.last_save_time=time.time()

    def __tarred_value(self, raw_value):
        return raw_value - self.offset

    def calibrate(self, raw_value, weight):
        tarred_value = self.__tarred_value(raw_value)
        self.factor = weight / tarred_value

    def __calibrated_value(self, tarred_value) -> float:
        return tarred_value * self.factor

    def weight(self, raw_value) -> float:
        tarred_value = self.__tarred_value(raw_value)
        return self.__calibrated_value(tarred_value)

    def print(self):
        print(f"offset={self.offset}\tfactor={self.factor}\t")


# TEST
if __name__ == "__main__":
    raw_value = 50

    calibration = ScaleSensorCalibration()
    calibration.tarre(raw_value)

    # increase of 20 is actual weight of 10g
    raw_value = raw_value + 20
    calibration.calibrate(raw_value, 10)

    print(calibration.weight(raw_value))  # 10g
    print(calibration.weight(raw_value + 20))  # 20g

    calibration.print()

db.create_tables([ScaleSensorCalibration])
