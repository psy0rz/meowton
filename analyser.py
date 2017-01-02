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
    '''to calculate weights from raw data and do stuff like auto tarring and averaging'''

    def __init__(self, calibrate_weight, calibrate_factors):

        self.calibrate_weight=calibrate_weight
        self.calibrate_factors=calibrate_factors


        #range in grams in which the scale should stay to be considered "stable"
        self.stable_range=50

        # number of measurement to allow scale sensors to recover before starting to average
        # after a heavy weight is removed from a scale, it takes some times for the weight-modules to "bend back"
        self.stable_skip_measurements=100

        # number of measurements averaging after which to auto tarre
        self.stable_auto_tarre=6000

        # #stable measurements and tarring only below this weight
        # self.stable_below=1000


        self.sensor_count=len(calibrate_factors)
        self.stable_reset()


        self.no_tarre=True
        self.offsets=[]
        for i in range(0, self.sensor_count):
            self.offsets.append(0)

        #last sensor readings
        self.current=[]

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

    def get_current(self):
        return(self.current)

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
        self.current=sensors


        #do auto tarring after a long stable period
        if (self.stable_totals_count>self.stable_auto_tarre)  or (self.no_tarre and self.stable_totals_count>10):
            self.offsets=self.get_average()
            self.stable_reset()
            self.no_tarre=False


    def offset(self, sensors):
        '''return offsetted values of specified raw sensor values'''
        ret=[]
        sensor_nr=0
        for sensor in sensors:
            ret.append(sensor - self.offsets[sensor_nr])
            sensor_nr=sensor_nr+1
        return(ret)


    def calibrated_weight(self, sensors):
        '''return calibrated weight value of specified raw sensor values (dont forget to offset first)'''
        weight=0
        sensor_nr=0
        for sensor in sensors:
            weight=weight+sensor*self.calibrate_weight/self.calibrate_factors[sensor_nr]
            sensor_nr=sensor_nr+1

        return(weight)


class Catalyser():
    '''try to track the weights of several cats during eating. catalyser works with weights instead of raw sensor values'''

    def __init__(self):
        self.average_last=0
        self.average_prev=0
        self.average_count=0
        self.graph_measurements=[]

        #measure enter and exist weights and eating time
        self.enter_weight=0
        self.exit_weight=0
        self.eat_time=0
        pass

    def update(self, scale):

        #keep graph of last measuremens
        self.graph_measurements.append(int(scale.calibrated_weight(scale.offset(scale.get_current()))))
        if (len(self.graph_measurements)>600):
            self.graph_measurements.pop(0)

        #is there a stable average
        if scale.get_average_count():

            average_current=int(scale.calibrated_weight(scale.offset(scale.get_average())))
            #the average is still changing
            if average_current!=self.average_last:
                self.average_count=0
                self.average_last=average_current
            #average stayed the same since last measurement
            else:
                self.average_count=self.average_count+1

                #average stayed the same for a number of measurements
                if self.average_count==100:
                    diff=average_current-self.average_prev

                    #change was at least the size of a cat?:
                    if abs(diff)>1000:
                        if diff>0:
                            print("Jumped on ,", diff)
                        else:
                            print("Jumped off,", abs(diff))

                        print(self.graph_measurements)
                        print()
                        self.average_prev=average_current





scale=Scale(


    calibrate_weight=1074 *1534/ 1645,
    calibrate_factors=[
        402600,
        428500,
        443400,
        439700,
    ]
)

catalyser=Catalyser()

sort_index=[ ( 'timestamp', pymongo.ASCENDING ) , ( 'nr' , pymongo.ASCENDING ) ]

db.measurements.create_index(sort_index)


for doc in db.measurements.find(
    filter=
    { 'timestamp':
        { '$gte': int(time.time())-(8*3600)
        }
    }
    ).sort(sort_index):


    scale.measurement(doc['sensors'])
    catalyser.update(scale)
