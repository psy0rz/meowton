#!/usr/bin/env python3

import re
import traceback
# import json
import sys
import os.path
import time

import pymongo
import bson.objectid
from config import db


class Scale:

    def __init__(self, calibrate_weight, calibrate_factors):

        self.calibrate_weight=calibrate_weight
        self.calibrate_factors=calibrate_factors


        #range in grams in which the scale should stay to be considered "stable"
        self.stable_range=50

        # number of measurement to allow scale sensors to recover before starting to average
        # after a heavy weight is removed from a scale, it takes some times for the weight-modules to "bend back"
        self.stable_skip_measurements=100

        # number of measurements averaging after which to auto tarre
        self.stable_auto_tarre=600

        #stable measurements and tarring only below this weight
        self.stable_below=1000


        self.sensor_count=len(calibrate_factors)
        self.stable_reset()

        #we just started, make sure we tarre quickly
        self.stable_count=self.stable_auto_tarre-30

        self.no_tarre=True
        self.offsets=[]
        for i in range(0, self.sensor_count):
            self.offsets.append(0)


    def stable_reset(self):
        self.stable_min=100000000
        self.stable_max=-100000000
        self.stable_count=0
        self.stable_totals=[]
        self.stable_totals_count=0


        for i in range(0, self.sensor_count):
            self.stable_totals.append(0)


    def get_average(self):
        '''gets raw average values since of this stable period'''
        ret=[]
        for total in self.stable_totals:
            ret.append(int(total/self.stable_totals_count))
        return(ret)

    def get_average_count(self):
        '''number of samples the current average is caculated over'''
        return(self.stable_totals_count)


    def stable_measurement(self,sensors):
        '''determine if scale is stabilised and calculates average. '''

        weight=self.calibrated_weight(sensors)

        if weight<self.stable_min:
            self.stable_min=weight

        if weight>self.stable_max:
            self.stable_max=weight

        if (self.stable_max - self.stable_min) < self.stable_range:
            self.stable_count=self.stable_count+1
        else:
            self.stable_reset()

        #do averaging after skipping the first measurements because of scale drifting and recovery
        if self.stable_count>=self.stable_skip_measurements:
                sensor_nr=0
                for sensor in sensors:
                    self.stable_totals[sensor_nr]=self.stable_totals[sensor_nr]+sensor
                    sensor_nr=sensor_nr+1

                self.stable_totals_count=self.stable_totals_count+1


    def measurement(self, sensors):
        self.stable_measurement(sensors)


        #do auto tarring after a long stable period
        if self.stable_totals_count>self.stable_auto_tarre or (self.no_tarre and self.stable_totals_count>10):
            self.offsets=self.get_average()
            self.stable_reset()
            self.no_tarre=False


    def offset(self, sensors):
        '''return offsetted values of specified sensor value'''
        ret=[]
        sensor_nr=0
        for sensor in sensors:
            ret.append(sensor - self.offsets[sensor_nr])
            sensor_nr=sensor_nr+1
        return(ret)


    def calibrated_weight(self, sensors):
        '''return calibrated weight value of specified sensor values (dont forget to offset first)'''
        weight=0
        sensor_nr=0
        for sensor in sensors:
            weight=weight+sensor*self.calibrate_weight/self.calibrate_factors[sensor_nr]
            sensor_nr=sensor_nr+1

        return(weight)


scale=Scale(


    calibrate_weight=1074 *1534/ 1645,
    calibrate_factors=[
        402600,
        428500,
        443400,
        439700,
    ]
)




prev_value=0
skipped=0
count=0


sort_index=[ ( 'timestamp', pymongo.ASCENDING ) , ( 'nr' , pymongo.ASCENDING ) ]

db.measurements.create_index(sort_index)

count=0
for doc in db.measurements.find(
    filter=
    { 'timestamp':
        { '$gte': int(time.time())-(3*3600)
        }
    }
    ).sort(sort_index):


    scale.measurement(doc['sensors'])
    #
    value=int(scale.calibrated_weight(scale.offset(doc['sensors'])))

    if (scale.stable_totals_count):
        avg_value=int(scale.calibrated_weight(scale.offset(scale.get_average())))
        totals=scale.get_average_count()
    else:
        avg_value=0
        totals=0



    count=count+1
    if value==prev_value:
        skipped=skipped+1
    else:
        # if skipped:
        #     print("SKIPPED", skipped)
        print(value, avg_value, totals)
        prev_value=value
        skipped=0
