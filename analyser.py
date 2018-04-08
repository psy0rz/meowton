#!/usr/bin/env python3

### dependencys in ubuntu:

# sudo apt-get install python3-matplotlib python3-scipy python3-pymongo python3-gdbm python3-influxdb


import re
import traceback
# import json
import sys
import os.path
import time

import config

# import collections
# import matplotlib
# matplotlib.use('Agg')
# from scipy.interpolate import interp1d
# import matplotlib.pyplot as plt
import shelve
# import scipy
import bottle
import re

import urllib.request
import argparse
import yaml

class Scale:
    '''to calculate weights from raw data and do stuff like auto tarring and averaging

    generates events for every stable measurement via measurement_callback
    '''

    def __init__(self, calibrate_weight, calibrate_factors, callback, annotation_callback):

        self.state={}


        self.calibrate_weight=calibrate_weight
        self.calibrate_factors=calibrate_factors
        self.callback=callback
        self.annotation_callback=annotation_callback


        # range in grams in which the scale should stay to be considered "stable"
        self.stable_range=50

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

        self.__stable_reset(0)


        #tarre offsets
        self.state['no_tarre']=True
        self.state['offsets']=[]
        for i in range(0, self.sensor_count):
            self.state['offsets'].append(0)

        #last sensor readings
        self.state['current']=[]

    def __stable_reset(self, weight):
        self.state['stable_min']=weight
        self.state['stable_max']=weight
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
            self.__stable_reset(weight)
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
            self.__stable_reset(weight)

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

        # generate measuring event, every stable_wait measurements
        if self.state['stable_count']>0 and self.state['stable_count'] % self.stable_wait == 0:
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
        # self.state['enter_weight']=0
        # self.state['enter_time']=0

        #all valid weights of this on-scale period
        # self.state['valid_weights']=[];

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
            self.callback(timestamp, self.find_cat(weight), weight)
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
            if abs(cat['weight']-weight)<500:
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


    def __init__(self,db):

        self.previous_annotation=""
        self.scale=Scale(
            calibrate_weight=1074 *1534/ 1645,
            calibrate_factors=[
                402600,
                428500,
                443400,
                439700,
            ],
            callback=self.measurement_event,
            annotation_callback=self.annotation_event
        )

        self.catalyser=Catalyser(callback=self.catalyser_event)

        self.last_save=time.time()
        self.db_timestamp=0

        self.load_state()

        #db shizzle
        self.client=db

        self.points_batch=[]

        self.last_feed_time=0

        self.realtime=False


    def save_state(self):
        '''save current state so we can resume later when new measurements have arrived'''
        with shelve.open("analyser.state") as shelve_db:
            shelve_db['scale_state']=self.scale.state
            shelve_db['catalyser_state']=self.catalyser.state
            shelve_db['db_timestamp']=self.db_timestamp


        state={
            'scale_state'    : self.scale.state,
            'catalyser_state' : self.catalyser.state,
            'db_timestamp'    : self.db_timestamp
        }
        with open("analyser.yaml","w") as fh:
            fh.write(yaml.dump(state, default_flow_style=False))


    def load_state(self):
        with shelve.open("analyser.state") as shelve_db:
            if 'db_timestamp' in shelve_db:
                self.scale.state=shelve_db['scale_state']
                self.catalyser.state=shelve_db['catalyser_state']
                self.db_timestamp=shelve_db['db_timestamp']


    def annotation_event(self,timestamp,message):
        # if message==self.previous_annotation:
        #     return
        # self.previous_annotation=message

        print(timestamp, message)
        self.points_batch.append({
            "measurement": "annotations",
            "time": timestamp,
            "fields":{
                        'title': message,
                        'tags': "error"
                    }
        })


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



    def feed(self, amount):
        """despend amount of food"""
        if self.realtime:
            try:
                urllib.request.urlopen('http://192.168.13.58/control?cmd=feed,1')
            except Exception as e:
                pass


    def catalyser_event(self, timestamp, cat, weight):
        """cat weighing event detected"""
        print("{}: {} detected at {} gram".format(time.ctime(self.db_timestamp/1000), cat['name'], int(weight)))




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


        # feed tracy as much as she wants :P
        if cat['name']=='Cat 0' and time.time()-self.last_feed_time>=60:
            print("Feeding tracy")
            self.last_feed_time=time.time()
            # self.feed(1)


    def housekeeping(self,force=False):
        """regular saves and batched writing"""

        if force or time.time()-self.last_save>10:
            if self.points_batch:
                # print("Writing to influxdb, processed up to: ", time.ctime(self.db_timestamp/1000))
                self.client.write_points(points=self.points_batch, time_precision="ms")
                self.points_batch=[]

            self.save_state()
            self.last_save=time.time()


    def analyse_measurement(self, timestamp, measurement):
        '''analyse one measurement and store results (time in mS)'''

        self.db_timestamp=timestamp

        self.scale.measurement(timestamp,measurement)
        # catalyser.update(scale, time["timestamp"])

        # store all calculated weights (for analyses and debugging with grafana)
        self.points_batch.append({
            "measurement": "weights",
            "time": timestamp,
            "fields":{
                        'weight': self.scale.calibrated_weight(self.scale.offset(measurement))
                    }
        })

        self.points_batch.append({
            "measurement": "stable_count",
            "time": timestamp,
            "fields":{
                        'stable_count': self.scale.state['stable_count']
                    }
        })

        self.housekeeping()

    def analyse_all(self, reanalyse_days=None):
        '''analyse all existing measurements, in a resumable way.'''
        analysed_measurement_names=["events", "weights", "cats", "cats_debug", "annotations",  "stable_count" ]
        if not self.db_timestamp:
            #drop and recalculate everything
            print("Deleting all analysed data")
            for analysed_measurement_name in analysed_measurement_names:
                self.client.query("drop measurement {}".format(analysed_measurement_name))

        if reanalyse_days!=None:
            print("Deleting last {} days of analysed data".format(reanalyse_days))
            self.db_timestamp=int((time.time()-reanalyse_days*24*3600)*1000) # mS
            for analysed_measurement_name in analysed_measurement_names:
                self.client.query("delete from  {} WHERE time > {}".format(analysed_measurement_name, self.db_timestamp))


        print("Resuming from: ", time.ctime(self.db_timestamp/1000))

        for result in self.client.query("select * from raw_sensors where time>"+str(self.db_timestamp*1000000), database="meowton", stream=True, chunked=True, chunk_size=10000, epoch='ms'):
            for point in result.get_points():

                measurement=[
                    point['sensor0'],
                    point['sensor1'],
                    point['sensor2'],
                    point['sensor3'],
                ]

                self.analyse_measurement(point['time'], measurement)



        #flush/save last stuff
        self.housekeeping(force=True)

        print("Analyses complete, waiting for new measurement")
        self.realtime=True


# handle new measurement data
@bottle.post('/raw')
def post_raw():

    # session = bottle.request.environ.get('beaker.session')

    #result will be stored here:
    result = {}

    try:
        #to see what kind of body the server receives, for debugging purposes:
        # print ("HEADERS: ", dict(bottle.request.headers))
        # print ("BODY: ", bottle.request.body.getvalue())
        # print ("FILES: ", dict(bottle.request.files))
        # print ("FORMS:", dict(bottle.request.forms))
        # print ("CONTENTTYPE", request.content-type)


        if bottle.request.headers["content-type"].find("application/json")==0:
            measurements = bottle.request.json
            current_timestamp=time.time() # in S
            measurement_nr=0
            for measurement in measurements:
                timestamp=current_timestamp+measurement_nr*0.1
                # store raw data so we can reanalyse if we change our algo.
                meowton.points_batch.append(
                    {
                        "measurement": "raw_sensors",
                        "time": int(timestamp*1000), # in mS
                        "fields":{
                                    'sensor0': measurement[0],
                                    'sensor1': measurement[1],
                                    'sensor2': measurement[2],
                                    'sensor3': measurement[3]
                                }
                    }
                )
                meowton.analyse_measurement(int(timestamp*1000), measurement) # in mS
                measurement_nr=measurement_nr+1



    except Exception as e:
        print("Error: "+str(e)+"\n")
        print(bottle.request.body.getvalue())


### parse args

parser = argparse.ArgumentParser(description='Meowton v1.0')
# parser.add_argument('--ssh-source', default="local", help='Source host to get backup from. (user@hostname) Default %(default)s.')
# parser.add_argument('--ssh-target', default="local", help='Target host to push backup to. (user@hostname) Default  %(default)s.')
# parser.add_argument('--ssh-cipher', default=None, help='SSH cipher to use (default  %(default)s)')
# parser.add_argument('--keep-source', type=int, default=30, help='Number of days to keep old snapshots on source. Default %(default)s.')
# parser.add_argument('--keep-target', type=int, default=30, help='Number of days to keep old snapshots on target. Default %(default)s.')
# parser.add_argument('backup_name',    help='Name of the backup (you should set the zfs property "autobackup:backup-name" to true on filesystems you want to backup')
# parser.add_argument('target_fs',    help='Target filesystem')
#
# parser.add_argument('--no-snapshot', action='store_true', help='dont create new snapshot (usefull for finishing uncompleted backups, or cleanups)')
# parser.add_argument('--no-send', action='store_true', help='dont send snapshots (usefull to only do a cleanup)')
# parser.add_argument('--resume', action='store_true', help='support resuming of interrupted transfers by using the zfs extensible_dataset feature (both zpools should have it enabled)')
#
# parser.add_argument('--strip-path', default=0, type=int, help='number of directory to strip from path (use 1 when cloning zones between 2 SmartOS machines)')
#
#
# parser.add_argument('--destroy-stale', action='store_true', help='Destroy stale backups that have no more snapshots. Be sure to verify the output before using this! ')
# parser.add_argument('--clear-refreservation', action='store_true', help='Set refreservation property to none for new filesystems. Usefull when backupping SmartOS volumes. (recommended)')
# parser.add_argument('--clear-mountpoint', action='store_true', help='Sets canmount=noauto property, to prevent the received filesystem from mounting over existing filesystems. (recommended)')
# parser.add_argument('--rollback', action='store_true', help='Rollback changes on the target before starting a backup. (normally you can prevent changes by setting the readonly property on the target_fs to on)')
#
#
# parser.add_argument('--compress', action='store_true', help='use compression during zfs send/recv')
parser.add_argument('--reanalyse', help='Reanalyse last X days.', type=int)
# parser.add_argument('--test', action='store_true', help='dont change anything, just show what would be done (still does all read-only operations)')
# parser.add_argument('--verbose', action='store_true', help='verbose output')
# parser.add_argument('--debug', action='store_true', help='debug output (shows commands that are executed)')

#note args is the only global variable we use, since its a global readonly setting anyway
args = parser.parse_args()


# initialize
meowton=Meowton(config.db)

# make sure we're uptodate with the analyser
meowton.analyse_all(args.reanalyse)

# start server
application=bottle.default_app()
bottle.run(quiet=True,reloader=False, app=application, host='0.0.0.0', port=8080)
