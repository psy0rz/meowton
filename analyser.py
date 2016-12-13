#!/usr/bin/env python3

import re
import traceback
# import json
import sys
import os.path
import time




class Scale:

    def __init__(self, calibrate_weight, calibrate_factors):
        self.calibrate_weight=calibrate_weight
        self.calibrate_factors=calibrate_factors
        self.sensor_count=len(calibrate_factors)
        self.stable_reset()

        self.offsets=[]
        for i in range(0, self.sensor_count):
            self.offsets.append(0)


    def stable_reset(self):
        self.stable_min=100000000
        self.stable_max=-100000000
        self.stable_count=0
        self.stable_range=2000
        self.stable_totals=[]


        for i in range(0, self.sensor_count):
            self.stable_totals.append(0)


    def get_average(self):
        '''gets raw average values since of this stable period'''
        ret=[]
        for total in self.stable_totals:
            ret.append(int(total/self.stable_count))
        return(ret)


    def stable_measurement(self,sensors):
        '''determine if scale is stabilised and calculates average. this is for static loads (not cats ;) and tarring'''
        total=0
        sensor_nr=0
        for sensor in sensors:
            total=total+sensor
            self.stable_totals[sensor_nr]=self.stable_totals[sensor_nr]+sensor
            sensor_nr=sensor_nr+1

        if total<self.stable_min:
            self.stable_min=total

        if total>self.stable_max:
            self.stable_max=total

        if (self.stable_max - self.stable_min) < self.stable_range:
            self.stable_count=self.stable_count+1
        else:
            self.stable_reset()




    def measurement(self, sensors):
        self.stable_measurement(sensors)

        #do not average for too long and also do auto tarring
        if self.stable_count>600:
            self.offsets=self.get_average()
            self.stable_reset()


    def offset(self, sensors):
        '''return offsetted values of specified sensor value'''
        ret=[]
        sensor_nr=0
        for sensor in sensors:
            ret.append(sensor - self.offsets[sensor_nr])
            sensor_nr=sensor_nr+1
        return(ret)

scale=Scale(
    calibrate_weight=1074,
    calibrate_factors=[
        402600,
        428500,
        443400,
        439700,
    ]
)





with open('measurements.csv','r') as fh:
    for line in fh:
        # print(line)
        (timestamp, *sensor_strs)=line.rstrip(";\n").split(";")

        #make ints
        sensors=[]
        for sensor_str in sensor_strs:
            sensors.append(int(sensor_str))

        print("raw: ",sensors)
        scale.measurement(sensors)
        if (scale.stable_count):
            print("avg:" ,scale.stable_count, scale.offset(scale.get_average()))
