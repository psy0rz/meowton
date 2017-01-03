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
import collections

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
        self.__stable_reset()


        self.no_tarre=True
        self.offsets=[]
        for i in range(0, self.sensor_count):
            self.offsets.append(0)

        #last sensor readings
        self.current=[]

    def __stable_reset(self):
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


    def __stable_measurement(self,sensors):
        '''determine if scale is stabilised and calculates average. '''

        weight=self.calibrated_weight(sensors)

        if weight<self.stable_min:
            self.stable_min=weight

        if weight>self.stable_max:
            self.stable_max=weight

        if (self.stable_max - self.stable_min) < self.stable_range:
            self.stable_count=self.stable_count+1
        else:
            self.__stable_reset()

        #do averaging after skipping the first measurements because of scale drifting and recovery
        if self.stable_count>=self.stable_skip_measurements:
                sensor_nr=0
                for sensor in sensors:
                    self.stable_totals[sensor_nr]=self.stable_totals[sensor_nr]+sensor
                    sensor_nr=sensor_nr+1

                self.stable_totals_count=self.stable_totals_count+1


    def measurement(self, sensors):
        self.__stable_measurement(sensors)
        self.current=sensors


        #do auto tarring after a long stable period
        if (self.stable_totals_count>self.stable_auto_tarre)  or (self.no_tarre and self.stable_totals_count>10):
            self.offsets=self.get_average()
            self.__stable_reset()
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
        self.graph_measurements=collections.deque([],3000)
        self.graph_averages=collections.deque([],3000)

        #measure enter and exist weights and eating time
        self.enter_weight=0
        self.enter_time=0
        self.enter_index=0
        self.exit_weight=0

        #per cat data
        doc=db.settings.find_one({ 'name': 'cats' })

        self.cats=[]

        pass



    def update(self, scale, timestamp):
        '''update with current state of scale'''

        #keep graph of last measuremenst
        self.graph_measurements.append(int(scale.calibrated_weight(scale.offset(scale.get_current()))))
        self.enter_index=self.enter_index+1

        #is there a stable average
        if scale.get_average_count():

            average_current=int(scale.calibrated_weight(scale.offset(scale.get_average())))
            self.graph_averages.append(average_current)

            #the average is still changing
            if average_current!=self.average_last:
                self.average_count=0
                self.average_last=average_current
            #average stayed the same since last measurement
            else:
                self.average_count=self.average_count+1

                #average stayed the same for a number of measurements
                if self.average_count==100:

                    #determine difference with previous stable average
                    diff=average_current-self.average_prev
                    self.average_prev=average_current

                    #record the change-event
                    self.__event(diff, timestamp)

        else:
            self.graph_averages.append(None)


    def __event(self, diff, timestamp):
        '''records change event'''

        #only record cat-sized changes :)
        if abs(diff)<1000:
            return

        #cat entered
        if diff>0:
            self.enter_time=timestamp
            self.enter_weight=diff
            self.enter_index=0


        #cat exited
        else:
            self.exit_weight=abs(diff)

            errors=[]

            #if it took too long we probably missed something
            timediff=timestamp-self.enter_time
            consumed=self.exit_weight-self.enter_weight

            if timestamp-self.enter_time>6000:
                errors.append("Cat took too long.".format())

            #cat can only stay the same weight or get heavier while eating.
            #if it got much lighter the measurements are wrong
            if self.exit_weight-self.enter_weight<-2:
                errors.append("Cat got lighter while eating somehow.")

            if self.exit_weight-self.enter_weight>100:
                errors.append("Cat ate impossible amount: {}g".format(consumed))

            #determine which cat it is
            cat=self.__find_cat(self.enter_weight)
            if cat:
                #update moving average weight to not lose track of cat
                cat['weight']=int(cat['weight']*0.9 + self.enter_weight*0.1)
            else:
                #new cat
                cat={
                    'weight': self.enter_weight,
                    'name': "Cat "+str(len(self.cats))
                }
                self.cats.append(cat)

            print("Date            :", time.ctime(timestamp))
            print("Name            :", cat['name'])
            print("Cat enter weight:", self.enter_weight)
            print("Cat exit  weight:", self.exit_weight)
            print("Food consumed   :", consumed)
            print("Eating time     :", timediff)
            print("Errors          :", errors)
            # print(self.graph_measurements)
            print()


            ######### graph
            import matplotlib.pyplot as plt

            entered_x=len(self.graph_measurements)-self.enter_index
            if entered_x<0:
                entered_x=0

            exit_x=len(self.graph_measurements)-1

            plt.annotate(
                'Entered at {}g'.format(self.enter_weight),
                xy=(entered_x, self.graph_averages[entered_x]),
                xytext=(entered_x-100, self.graph_averages[entered_x]-500),
                arrowprops=dict(color='gray', width=0.1, headwidth=5),
                )

            plt.annotate(
                'Exitted at {}g'.format(self.exit_weight),
                xy=(exit_x, self.graph_averages[exit_x]),
                xytext=(exit_x-1000, self.graph_averages[exit_x]+500),
                arrowprops=dict(color='gray', width=0.1, headwidth=5),
                )

            plt.suptitle("{} ({})".format(cat['name'], time.ctime(timestamp)))

            if errors:
                plt.title("Error: "+" ".join(errors)).set_color('red')

            else:
                plt.title("Ate {}g in {} seconds".format(consumed, timediff))


            #graphs and labels
            plt.plot(self.graph_measurements,color='black')
            plt.plot(self.graph_averages, color='red')
            plt.ylabel('Weight (g)')
            plt.xlabel('Measurement number')

            plt.savefig("graphs/{}.png".format(timestamp))
            plt.close()


            self.enter_weight=0
            self.enter_time=0

    def __find_cat(self, weight):
        '''try to find a cat by weight'''

        for cat in self.cats:
            #max differnce gram for now
            if abs(cat['weight']-weight)<100:
                return(cat)

        return(None)


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
        { '$gte': int(time.time())-(24*3600*5)
        }
    }
    ).sort(sort_index):


    scale.measurement(doc['sensors'])
    catalyser.update(scale, doc["timestamp"])
