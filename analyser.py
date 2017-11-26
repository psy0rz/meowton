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


        #range in grams in which the scale should stay to be considered "stable"
        self.stable_range=25

        # number of measurement to allow scale sensors to recover before starting to average
        # after a heavy weight is removed from a scale, it takes some times for the weight-modules to "bend back"
        self.stable_skip_measurements=10

        # for how many measurements should the scale be in the stable_range to be considered stable?
        # at this point it will generate a measurement event by calling the callback
        self.stable_wait=20

        # number of measurements averaging after which to auto tarre
        self.stable_auto_tarre=6000

        # #stable measurements and tarring only below this weight
        # self.stable_below=1000


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
        """update measurent data and generate stable events when detected"""

        self.state['current']=sensors

        #calculate weight, without offsetting since we're only using it for stability determination
        weight=self.calibrated_weight(sensors)

        # store stability statistics
        if weight<self.state['stable_min']:
            self.state['stable_min']=weight

        if weight>self.state['stable_max']:
            self.state['stable_max']=weight

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

        # do auto tarring (quick the first time, after that it takes stable_auto_tarre measurements)
        if (self.state['stable_totals_count'] == self.stable_auto_tarre)  or (self.state['no_tarre'] and self.state['stable_totals_count'] == 10):
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
    '''try to track the weights of several cats during eating. catalyser works with weights instead of raw sensor values'''

    def __init__(self):
        self.state={}

        self.state['average_last']=0
        self.state['average_prev']=0
        self.state['average_count']=0
        self.state['graph_measurements']=collections.deque([],3000)
        self.state['graph_averages']=collections.deque([],3000)

        #measure enter and exist weights and eating time
        self.state['enter_weight']=0
        self.state['enter_time']=0
        self.state['enter_index']=0
        self.state['exit_weight']=0


        #per cat data
        self.state['cats']=[]

        pass



    def update(self, scale, timestamp):
        '''update with current state of scale'''

        #keep graph of last measuremenst
        self.state['graph_measurements'].append(int(scale.calibrated_weight(scale.offset(scale.get_current()))))
        self.state['enter_index']=self.state['enter_index']+1

        #is there a stable average
        if scale.get_average_count():

            average_current=int(scale.calibrated_weight(scale.offset(scale.get_average())))
            self.state['graph_averages'].append(average_current)

            #the average is still changing
            if average_current!=self.state['average_last']:
                self.state['average_count']=0
                self.state['average_last']=average_current
            #average stayed the same since last measurement
            else:
                self.state['average_count']=self.state['average_count']+1

                #average stayed the same for a number of measurements
                if self.state['average_count']==10:

                    #determine difference with previous stable average
                    diff=average_current-self.state['average_prev']
                    self.state['average_prev']=average_current

                    #record the change-event
                    self.__event(diff, timestamp)

        else:
            self.state['graph_averages'].append(None)


    def __event(self, diff, timestamp):
        '''records change event'''

        #only record cat-sized changes :)
        if abs(diff)<1000:
            return

        #cat entered
        if diff>0:
            self.state['enter_time']=timestamp
            self.state['enter_weight']=diff
            self.state['enter_index']=0


        #cat exited
        else:
            self.state['exit_weight']=abs(diff)

            errors=[]

            #if it took too long we probably missed something
            timediff=timestamp-self.state['enter_time']
            consumed=self.state['exit_weight']-self.state['enter_weight']

            if timestamp-self.state['enter_time']>6000:
                errors.append("Cat took too long.".format())

            #cat can only stay the same weight or get heavier while eating.
            #if it got much lighter the measurements are wrong
            if self.state['exit_weight']-self.state['enter_weight']<-2:
                errors.append("Cat got lighter while eating somehow.")

            if self.state['exit_weight']-self.state['enter_weight']>100:
                errors.append("Cat ate impossible amount: {}g".format(consumed))

            #determine which cat it is
            cat=self.__find_cat(self.state['enter_weight'])
            #update moving average weight to not lose track of cat
            if not errors:
                cat['weight']=int(cat['weight']*0.9 + self.state['enter_weight']*0.1)
                cat['count']=cat['count']+1

            print("Date            :", time.ctime(timestamp))
            print("Name            :", cat['name'])
            print("Cat enter weight:", self.state['enter_weight'])
            print("Cat exit  weight:", self.state['exit_weight'])
            print("Food consumed   :", consumed)
            print("Eating time     :", timediff)
            print("Errors          :", errors)
            print()

            ######### save to event db

            db.events.insert({
                'name': cat['name'],
                'timestamp'   : timestamp,
                'enter_weight': self.state['enter_weight'],
                'exit_weight' : self.state['exit_weight'],
                'timediff'    : timediff,
                'errors'      : errors,
                'consumed'    : consumed
            })


            ######### graph

            entered_x=len(self.state['graph_measurements'])-self.state['enter_index']
            if entered_x<0:
                entered_x=0

            exit_x=len(self.state['graph_measurements'])-1

            fig, ax = plt.subplots()
            ax.yaxis.grid(True)

            plt.annotate(
                'Entered at {}g'.format(self.state['enter_weight']),
                xy=(entered_x, self.state['graph_measurements'][entered_x]),
                xytext=(entered_x-100, self.state['graph_measurements'][entered_x]-500),
                arrowprops=dict(color='gray', width=0.1, headwidth=5),
                )

            plt.annotate(
                'Exitted at {}g'.format(self.state['exit_weight']),
                xy=(exit_x, self.state['graph_measurements'][exit_x]),
                xytext=(exit_x-1000, self.state['graph_measurements'][exit_x]+500),
                arrowprops=dict(color='gray', width=0.1, headwidth=5),
                )

            plt.suptitle("{} ({})".format(cat['name'], time.ctime(timestamp)))

            if errors:
                plt.title("Error: "+" ".join(errors)).set_color('red')

            else:
                plt.title("Ate {}g in {} seconds".format(consumed, timediff))


            #graphs and labels
            plt.plot(self.state['graph_measurements'],color='black')
            plt.plot(self.state['graph_averages'], color='red')
            plt.ylabel('Weight (g)')
            plt.xlabel('Measurement number')

            plt.savefig("graphs/{}.png".format(timestamp))
            plt.close()

            self.state['enter_weight']=0
            self.state['enter_time']=0




    def __find_cat(self, weight):
        '''try to find a cat by weight'''

        best_match=None
        for cat in self.state['cats']:
            #max differnce gram for now
            if abs(cat['weight']-weight)<200:
                if not best_match or cat['count']>best_match['count']:
                    best_match=cat

        if best_match:
            return(best_match)

        #new cat
        cat={
            'weight': weight,
            'name': "Cat "+str(len(self.state['cats'])),
            'count': 0
        }
        self.state['cats'].append(cat)

        return(cat)


# sort_index=[ ( 'timestamp', pymongo.ASCENDING ) ]


# def global_graphs():
#     '''create global graphs from all the recorded events'''
#
#
#     weights={}
#     timestamps={}
#     for doc in db.events.find().sort(sort_index):
#         if not doc['errors']:
#
#             if doc['name'] not in weights:
#                 weights[doc['name']]=[]
#                 timestamps[doc['name']]=[]
#
#             weights[doc['name']].append(doc['enter_weight'])
#             timestamps[doc['name']].append(doc['timestamp'])
#
#
#     #traverse all cats
#     for name in weights.keys():
#         if len(weights[name])<5:
#             continue
#
#         fig, ax = plt.subplots()
#         plt.title(name)
#         plt.ylabel('Weight (g)')
#         plt.xlabel('Measurement date')
#         # x=matplotlib.dates.epoch2num(timestamps[name] + [ timestamps[name][len(timestamps[name])-1]+160000 ] )
#         x_values=matplotlib.dates.epoch2num(timestamps[name])
#
#         y_values=weights[name]
#         # ax.plot_date(x, y, 'k.')
#
#         # ax.plot_date(x, y)
#         #
#         # ravgs = [sum(y[i:i+5])/5. for i in range(len(y)-4)]
#         y_avgs=[]
#         y_prev=y_values[0]
#         smoothing=0.85  #percentage of previous value to use
#         for y_value in y_values:
#             y_prev=(y_prev* smoothing)+  (y_value * (1-smoothing))
#             y_avgs.append( y_prev  )
#
#         # print("waarden")
#         # print(x_values)
#         # print("gemmm")
#         # print(x_avgs)
#         # print()
#
#         ax.plot_date(x_values, y_values, color='gray', marker='.')
#         ax.plot(x_values, y_avgs, color='red', linewidth=2)
#         fig.autofmt_xdate()
#
#
#         fig.savefig("graphs/{}.png".format(name))
#         plt.close()
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

        self.catalyser=Catalyser()

        self.last_save=time.time()

        self.db_timestamp=self.load_state()

        #db shizzle
        self.client = influxdb.InfluxDBClient('localhost', 8086, database="meowton")
        self.client.create_database("meowton")

    def save_state(self, db_timestamp):
        '''save current state so we can resume later when new measurements have arrived'''
        with shelve.open("analyser.state") as shelve_db:
            shelve_db['scale_state']=self.scale.state
            shelve_db['catalyser_state']=self.catalyser.state
            shelve_db['db_timestamp']=db_timestamp

        print("Saved state ",timestamp)

    def load_state(self):
        with shelve.open("analyser.state") as shelve_db:
            if 'timestamp' in shelve_db:
                self.scale.state=shelve_db['scale_state']
                self.catalyser.state=shelve_db['catalyser_state']
                print("Resuming from state ", shelve_db['db_timestamp'])
                return(shelve_db['db_timestamp'])
            else:
                return(0)

    def measurement_event(self,timestamp, weight):
        print("jo", timestamp, weight)

    def run(self):
        '''analyse all new measurements since last time'''

        if not self.db_timestamp:
            #drop and recreate stuff
            self.client.query("drop database event", database="meowton", stream=True, chunked=True, chunk_size=1)

        doc=0
        for result in self.client.query("select * from raw_sensors", database="meowton", stream=True, chunked=True, chunk_size=10000, epoch='ms'):
            for point in result.get_points():
                print(point)
                measurement=[
                    point['sensor0'],
                    point['sensor1'],
                    point['sensor2'],
                    point['sensor3'],
                ]

                self.scale.measurement(point['time'],measurement)
                # catalyser.update(scale, time["timestamp"])

                if time.time()-self.last_save>10:
                    save_state(point['time'])
                    self.last_save=time.time()

        if doc:
            save_state(doc["timestamp"])




# analyse_measurements()
# global_graphs()


meowton=Meowton()
meowton.run()
