#!/usr/bin/env python3

### dependencys in ubuntu:

# sudo apt-get install python3-matplotlib python3-scipy python3-pymongo python3-gdbm python3-influxdb


import re
import traceback
# import json
import sys
import os.path
import time

import influxdb
import collections
import matplotlib
matplotlib.use('Agg')
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import shelve
import scipy



class Scale:
    '''to calculate weights from raw data and do stuff like auto tarring and averaging

    generates events for every stable measurement via measurement_callback
    '''

    def __init__(self, calibrate_weight, calibrate_factors, callback):

        self.state={}


        self.calibrate_weight=calibrate_weight
        self.calibrate_factors=calibrate_factors
        self.callback=callback


        # range in grams in which the scale should stay to be considered "stable"
        self.stable_range=25

        # max timegap between two measurements (ms)
        self.stable_max_timegap=5000
        self.state['last_timestamp']=0

        # number of measurement to allow scale sensors to recover before starting to average
        # after a heavy weight is removed from a scale, it takes some times for the weight-modules to "bend back"
        self.stable_skip_measurements=10

        # for how many measurements should the scale be in the stable_range to be considered stable?
        # at this point it will generate a measurement event by calling the callback
        self.stable_wait=50

        # number of measurements averaging after which to auto tarre
        self.stable_auto_tarre=100

        #max weight to tarre away (initial values will always be tarred)
        self.stable_auto_tarre_max=1000

        # #stable measurements and tarring only below this weight


        self.sensor_count=len(calibrate_factors)

        self.__stable_reset()


        #tarre offsets
        self.state['no_tarre']=True
        self.state['offsets']=[]
        for i in range(0, self.sensor_count):
            self.state['offsets'].append(0)

        #last sensor readings
        self.state['current']=[]

    def __stable_reset(self):
        self.state['stable_min']=100000000
        self.state['stable_max']=-100000000
        self.state['stable_count']=0
        self.state['stable_totals']=[]
        self.state['stable_totals_count']=0


        for i in range(0, self.sensor_count):
            self.state['stable_totals'].append(0)


    def get_average(self):
        '''gets raw average values since of this stable period'''
        ret=[]
        for total in self.state['stable_totals']:
            ret.append(int(total/self.state['stable_totals_count']))
        return(ret)

    def get_current(self):
        return(self.state['current'])

    def get_average_count(self):
        '''number of samples the current average is caculated over'''
        return(self.state['stable_totals_count'])


    # def __stable_measurement(self,sensors):
        # '''determine if scale is stabilised and calculates average. '''



    def measurement(self, timestamp, sensors):
        """update measurent data and generate stable events when detected. timestamp in ms """

        self.state['current']=sensors

        #calculate weight,
        weight=self.calibrated_weight(self.offset(sensors))


        # store stability statistics

        # reset stable measurement if there is a too big timegap
        if timestamp-self.state['last_timestamp']>self.stable_max_timegap:
            self.__stable_reset()
        self.state['last_timestamp']=timestamp

        # keep min/max values
        if weight<self.state['stable_min']:
            self.state['stable_min']=weight

        if weight>self.state['stable_max']:
            self.state['stable_max']=weight

        # reset if weight goes out of stable_range
        if (self.state['stable_max'] - self.state['stable_min']) < self.stable_range:
            self.state['stable_count']=self.state['stable_count']+1
        else:
            self.__stable_reset()

        # do averaging, but skip the first measurements because of scale drifting and recovery
        # note that we average the raw data for better accuracy
        if self.state['stable_count']>=self.stable_skip_measurements:
            sensor_nr=0
            for sensor in sensors:
                self.state['stable_totals'][sensor_nr]=self.state['stable_totals'][sensor_nr]+sensor
                sensor_nr=sensor_nr+1

            self.state['stable_totals_count']=self.state['stable_totals_count']+1

        # do auto tarring:
        # only under a certain weight and for a long stability period, or if its the first time do it quickly to get started
        if (
            (abs(weight)<self.stable_auto_tarre_max and (self.state['stable_totals_count'] == self.stable_auto_tarre)) or
            (self.state['no_tarre'] and self.state['stable_totals_count'] == 10)
        ):
            self.state['offsets']=self.get_average()
            self.state['no_tarre']=False

        # generate measuring event
        if self.state['stable_count'] == self.stable_wait:
            self.callback(timestamp, self.calibrated_weight(self.offset(self.get_average())) )




    def offset(self, sensors):
        '''return offsetted values of specified raw sensor values'''
        ret=[]
        sensor_nr=0
        for sensor in sensors:
            ret.append(sensor - self.state['offsets'][sensor_nr])
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
    '''cat analyser that tries to track the weights of several cats during eating'''

    def __init__(self, callback):

        self.callback=callback

        self.state={}

        # self.state['average_last']=0
        # self.state['average_prev']=0
        # self.state['average_count']=0
        # self.state['graph_measurements']=collections.deque([],3000)
        # self.state['graph_averages']=collections.deque([],3000)

        #measure enter and exist weights and eating time
        self.state['enter_weight']=0
        self.state['enter_time']=0

        #all valid weights of this on-scale period
        self.state['valid_weights']=[];

        # self.state['exit_weight']=0


        #per cat data
        self.state['cats']=[]

        # ignore stuff under this weight
        self.min_cat_weight=2000

        # if cat changes by this much while on scale, invalidate measurement
        self.on_scale_max_change=100

        pass



    def measurement_event(self, timestamp, weight):
        '''scale() detected a stable measurement. timestamp in ms, weight in grams. '''
        # cat on scale?
        if weight>self.min_cat_weight:
            self.callback(timestamp, self.find_cat(weight), weight, None)
        #     # just entered scale?
        #     if self.state['enter_time']==0:
        #         # start new measurement period
        #         self.state['enter_time']=timestamp
        #         self.state['enter_weight']=weight
        #         self.state['valid_weights']=[weight]
        #
        #     # was already on scale?
        #     else:
        #         #cat changed too much during this period?
        #         if abs(self.state['enter_weight']-weight)>self.on_scale_max_change:
        #             self.callback(timestamp, None, weight, "Cat changed too much, ignored measurements")
        #             self.state['enter_time']=0
        #         else:
        #             self.state['valid_weights'].append(weight)
        # # cat off scale?
        # else:
        #     # just left scale?
        #     if self.state['enter_time']:
        #         # end measurement
        #         self.state['enter_time']=0
        #         if len(self.state['valid_weights'])<0:
        #             self.callback(timestamp, None, weight, "Not enough valid measurements")
        #         else:
        #             avg_weight=0
        #             for w in self.state['valid_weights']:
        #                 avg_weight=avg_weight+w
        #             avg_weight=int(avg_weight/len(self.state['valid_weights']))
        #
        #
        #             self.callback(timestamp, self.__find_cat(avg_weight), avg_weight, None)
        #     # was already off scale?
        #     else:
        #         pass





        # #cat entered
        # if diff>0:
        #     self.state['enter_time']=timestamp
        #     self.state['enter_weight']=diff
        #     self.state['enter_index']=0
        #
        #
        # #cat exited
        # else:
        #     self.state['exit_weight']=abs(diff)
        #
        #     errors=[]
        #
        #     #if it took too long we probably missed something
        #     timediff=timestamp-self.state['enter_time']
        #     consumed=self.state['exit_weight']-self.state['enter_weight']
        #
        #     if timestamp-self.state['enter_time']>6000:
        #         errors.append("Cat took too long.".format())
        #
        #     #cat can only stay the same weight or get heavier while eating.
        #     #if it got much lighter the measurements are wrong
        #     if self.state['exit_weight']-self.state['enter_weight']<-2:
        #         errors.append("Cat got lighter while eating somehow.")
        #
        #     if self.state['exit_weight']-self.state['enter_weight']>100:
        #         errors.append("Cat ate impossible amount: {}g".format(consumed))
        #
        #     #determine which cat it is
        #     cat=self.__find_cat(self.state['enter_weight'])
        #     #update moving average weight to not lose track of cat
        #     if not errors:
        #         cat['weight']=int(cat['weight']*0.9 + self.state['enter_weight']*0.1)
        #         cat['count']=cat['count']+1
        #
        #     print("Date            :", time.ctime(timestamp))
        #     print("Name            :", cat['name'])
        #     print("Cat enter weight:", self.state['enter_weight'])
        #     print("Cat exit  weight:", self.state['exit_weight'])
        #     print("Food consumed   :", consumed)
        #     print("Eating time     :", timediff)
        #     print("Errors          :", errors)
        #     print()
        #
        #     ######### save to event db
        #
        #     db.events.insert({
        #         'name': cat['name'],
        #         'timestamp'   : timestamp,
        #         'enter_weight': self.state['enter_weight'],
        #         'exit_weight' : self.state['exit_weight'],
        #         'timediff'    : timediff,
        #         'errors'      : errors,
        #         'consumed'    : consumed
        #     })
        #
        #
        #
        #     self.state['enter_weight']=0
        #     self.state['enter_time']=0
        #



    def find_cat(self, weight, new=True):
        '''try to find a cat by weight'''

        best_match=None
        for cat in self.state['cats']:
            #max differnce gram for now
            if abs(cat['weight']-weight)<300:
                if not best_match or cat['count']>best_match['count']:
                    best_match=cat

        if best_match:
            #update moving average and count
            best_match['weight']=int(best_match['weight']*0.9 + weight*0.1)
            best_match['count']=best_match['count']+1

            return(best_match)

        if new:

            #new cat
            cat={
                'weight': weight,
                'name': "Cat "+str(len(self.state['cats'])),
                'count': 0
            }
            self.state['cats'].append(cat)

            return(cat)
        else:
            return(None)




class Meowton:


    def __init__(self):
        self.scale=Scale(
            calibrate_weight=1074 *1534/ 1645,
            calibrate_factors=[
                402600,
                428500,
                443400,
                439700,
            ],
            callback=self.measurement_event
        )

        self.catalyser=Catalyser(callback=self.catalyser_event)

        self.last_save=time.time()
        self.db_timestamp=0

        self.load_state()

        #db shizzle
        self.client = influxdb.InfluxDBClient('localhost', 8086, database="meowton")
        self.client.create_database("meowton")

        self.points_batch=[]

    def save_state(self):
        '''save current state so we can resume later when new measurements have arrived'''
        with shelve.open("analyser.state") as shelve_db:
            shelve_db['scale_state']=self.scale.state
            shelve_db['catalyser_state']=self.catalyser.state
            shelve_db['db_timestamp']=self.db_timestamp


    def load_state(self):
        with shelve.open("analyser.state") as shelve_db:
            if 'db_timestamp' in shelve_db:
                self.scale.state=shelve_db['scale_state']
                self.catalyser.state=shelve_db['catalyser_state']
                self.db_timestamp=shelve_db['db_timestamp']

    def measurement_event(self,timestamp, weight):
        """stable measurement detected"""

        self.points_batch.append({
            "measurement": "events",
            "time": timestamp,
            "fields":{
                        'weight': weight,
                    }
        })

        self.catalyser.measurement_event(timestamp, weight)

        #store all stable measurements per cat for debugging
        cat=self.catalyser.find_cat(weight, new=False)
        if cat:
            self.points_batch.append({
                "measurement": "cats_debug",
                "tags":{
                    "cat": cat['name']
                },
                "time": timestamp,
                "fields":{
                            'weight': weight,
                        }
            })



    def catalyser_event(self, timestamp, cat, weight, message):
        """cat weighing event detected"""
        # print("Cat event", cat, weight, message)

        if not message:
            self.points_batch.append({
                "measurement": "cats",
                "tags":{
                    "cat": cat['name']
                },
                "time": timestamp,
                "fields":{
                            'weight': weight,
                        }
            })
        else:
            self.points_batch.append({
                "measurement": "annotations",
                "time": timestamp,
                "fields":{
                            'title': message,
                            'tags': "error"
                        }
            })



    def housekeeping(self,force=False):
        """regular saves and batched writing"""

        if force or time.time()-self.last_save>1:
            if self.points_batch:
                print("Writing to influxdb, processed up to: ", time.ctime(self.db_timestamp/1000))
                self.client.write_points(points=self.points_batch, time_precision="ms")
                self.points_batch=[]

            self.save_state()
            self.last_save=time.time()


    def run(self):
        '''analyse all new measurements since last time'''

        if not self.db_timestamp:
            #drop and recalculate everything
            print("Delete all calculated data")
            self.client.query("drop measurement events; drop measurement weights; drop measurement cats; drop measurement cats_debug; drop measurement annotations", database="meowton")

        doc=0

        print("Resuming from: ", time.ctime(self.db_timestamp/1000))

        for result in self.client.query("select * from raw_sensors where time>"+str(self.db_timestamp*1000000), database="meowton", stream=True, chunked=True, chunk_size=10000, epoch='ms'):
            for point in result.get_points():
                self.db_timestamp=point['time']
                # print(point)
                measurement=[
                    point['sensor0'],
                    point['sensor1'],
                    point['sensor2'],
                    point['sensor3'],
                ]

                self.scale.measurement(point['time'],measurement)
                # catalyser.update(scale, time["timestamp"])

                # store all calculated weights (for analyses and debugging with grafana)
                self.points_batch.append({
                    "measurement": "weights",
                    "time": point['time'],
                    "fields":{
                                'weight': self.scale.calibrated_weight(self.scale.offset(measurement))
                            }
                })


            self.housekeeping()

        #flush/save last stuff
        self.housekeeping(force=True)



# analyse_measurements()
# global_graphs()


meowton=Meowton()
meowton.run()
