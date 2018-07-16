import urllib.request
import yaml
import os
import sys
import os.path
import time
import re
import re

from catalyser import Catalyser
from scale import Scale

class Meowton:


    def __init__(self,db):

        self.previous_annotation=""
        self.scale={}

        self.scale['cat']=Scale(
            calibrate_weight=1074 *1534/ 1645,
            calibrate_factors=[
                402600,
                428500,
                443400,
                439700,
            ],
            callback=self.cat_measurement_event,
            # annotation_callback=self.annotation_event
        )

        self.scale['food']=Scale(
            # calibrate_weight=1074 *1534/ 1645,

            calibrate_weight=44,
            calibrate_factors=[
                16657,
            ],
            callback=self.food_measurement_event,
            # annotation_callback=self.annotation_event
        )
        self.scale['food'].stable_range=1
        self.scale['food'].stable_auto_tarre_max=1
        self.scale['food'].stable_wait=10
        self.scale['food'].stable_auto_tarre=400 #make sure nothing is happening. dont make longer then idle-timeout in actual scale.


        self.catalyser=Catalyser(callback=self.catalyser_event)

        self.last_save=time.time()
        self.state={
            'db_timestamp': 0,
            #current food weight
            'food_weight': 0,
            #eaten food weight
            # 'food_sum': 0,
            'last_cat': None,
            'food_unknown': 0
        }


        self.load_state()

        #TODO: tarring away positive food-scale offsets is a problem, since we need to measure very small amounts
        self.scale['food'].tarre()

        #db shizzle
        self.client=db

        self.points_batch=[]

        self.last_feed_time=0

        self.realtime=False





    def save_state(self):
        '''save current state so we can resume later when new measurements have arrived'''

        state={
            'scale_state'       : self.scale['cat'].state,
            'food_scale_state'  : self.scale['food'].state,
            'catalyser_state'   : self.catalyser.state,
            'meowton_state'     : self.state,
        }

        with open("analyser.yaml.tmp","w") as fh:
            fh.write(yaml.dump(state, default_flow_style=False))

        os.rename("analyser.yaml.tmp", "analyser.yaml")


    def load_state(self):
        if os.path.isfile("analyser.yaml"):
            with open("analyser.yaml") as fh:
                state=yaml.load(fh.read())
                self.scale['cat'].state=state['scale_state']
                if 'food_scale_state' in state:
                    self.scale['food'].state=state['food_scale_state']

                self.catalyser.state=state['catalyser_state']
                self.state.update(state.get('meowton_state', {}))

    #
    # def annotation_event(self,timestamp,message):
    #     # if message==self.previous_annotation:
    #     #     return
    #     # self.previous_annotation=message
    #
    #     # print(timestamp, message)
    #     self.points_batch.append({
    #         "measurement": "annotations",
    #         "time": timestamp,
    #         "fields":{
    #                     'title': message,
    #                     'tags': "error"
    #                 }
    #     })




    def cat_measurement_event(self,timestamp, weight, new):
        """stable cat measurement detected"""

        self.points_batch.append({
            "measurement": "events",
            "time": timestamp,
            "tags":{
                "scale": "cat"
            },
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



    def food_measurement_event(self,timestamp, weight, new):
        """stable food measurement detected"""

        if new:
            self.points_batch.append({
                "measurement": "events",
                "time": timestamp,
                "tags":{
                    "scale": "food"
                },
                "fields":{
                            'weight': weight,
                        }
            })

            #how much food was eaten
            diff=self.state['food_weight']-weight

            #filter sudden increases, which are caused by dispencing a food portion
            if diff>-2:
                #no sudden increase, store diff as eaten food

                if self.state['last_cat']:
                    #some food aten by unknown cat?
                    if self.state['food_unknown']:
                        diff=diff+self.state['food_unknown']
                        self.state['food_unknown']=0

                    #substrace eaten food from quota
                    self.state['last_cat']['feed_quota']=self.state['last_cat']['feed_quota']-diff

                    #if someone feeds manual, make sure it doesnt go too low
                    if self.state['last_cat']['feed_quota']<-self.state['last_cat']['feed_max_quota']:
                        self.state['last_cat']['feed_quota']=-self.state['last_cat']['feed_max_quota']

                    self.points_batch.append({
                        "measurement": "food",
                        "tags":{
                            "cat": self.state['last_cat']['name']
                        },
                        "time": timestamp,
                        "fields":{
                                    'sum': float(diff),
                                }
                    })

                    print("Food weight {:.2f}g ({} ate {:.2f}g)".format(weight, self.state['last_cat']['name'],diff))
                else:
                    self.state['food_unknown']=self.state['food_unknown']+diff
                    print("Food weight {:.2f}g (unknown cat ate {:.2f}g)".format(weight, diff))

            else:
                print("Food weight {:.2f}g (changed {:.2f}g)".format(weight, diff))


            self.state['food_weight']=weight



    def feed(self):
        """dispend one portion of food"""
        if self.realtime:
            try:
                urllib.request.urlopen('http://192.168.13.58/control?cmd=feed,1')
            except Exception as e:
                pass


    def catalyser_event(self, timestamp, cat, weight):
        """cat weighing event detected (timestamp in mS)"""


        # #cat changed:
        # if self.state['last_cat']!=cat:
        #
        #     #there was a cat?
        #     if self.state['last_cat']:
        #         #then that one ate all the food
        #         if (self.state['food_sum']>=1):
        #             print("{} ate {:0.2f}g".format(self.state['last_cat']['name'], self.state['food_sum']))
        #             self.points_batch.append({
        #                 "measurement": "food",
        #                 "tags":{
        #                     "cat": self.state['last_cat']['name']
        #                 },
        #                 "time": timestamp,
        #                 "fields":{
        #                             'sum': float(self.state['food_sum']),
        #                         }
        #             })
        #
        #     else:
        #         print("Food change without cat:{:0.2f}g".format(self.state['food_sum']))
        #
        #     self.state['food_sum']=0
        #     self.state['last_cat']=cat
        self.state['last_cat']=cat


        # cat detected
        if cat:

            log="[ {} ] {} detected at {} gram: ".format(time.ctime(timestamp/1000), cat['name'], int(weight))

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


            # Autofeed this cat

            # feed:quota: current quota (when cat eats food it decreases. it increases with following parameters)
            # feed_daily: amount of food per day in gram (portions will be divided over the whole day)
            # feed_delay: time (in seconds) between individual portions from dispenser
            # feed_quota_max: maximum quota a cat can collect: we will never feed more than this amound of portions in one sessoin.

            # As long as the cat is on the scale, and there is quota left, it will feed a portion every 'feed_delay' seconds.


            if  'feed_daily' in cat:

                # set defaults if we just enabled it, or went back in time
                if not 'feed_quota_timestamp' in cat or cat['feed_quota_timestamp']>timestamp:
                    cat['feed_quota_timestamp']=timestamp
                    cat['feed_portion_timestamp']=timestamp
                    cat['feed_quota']=1

                # update food quota
                quota_add=(timestamp-cat['feed_quota_timestamp'])*cat['feed_daily']/(24*3600*1000)

                #time travelled
                if quota_add<0:
                    quota_add=0


                # print("timediff {}, quotadd {}".format(timestamp-cat['feed_quota_timestamp'],quota_add ))
                cat['feed_quota']=cat['feed_quota'] + quota_add
                    # instead of using the current timestamp, we calculate the timestamp based on the rounded quota_add number
                    # cat['feed_quota_timestamp']=cat['feed_quota_timestamp']+(quota_add * (cat['feed_rate']*60*1000))
                cat['feed_quota_timestamp']=timestamp
                if cat['feed_quota'] > cat['feed_max_quota']:
                    cat['feed_quota']=cat['feed_max_quota']


                # feed next portion?
                if self.state['food_weight']>1:
                    log=log+"Not feeding, still food in bowl. ({:0.2f}g quota left)".format(cat['feed_quota'])
                else:
                    if cat['feed_quota'] > 0:
                        last_feed_delta=int((timestamp-cat['feed_portion_timestamp'])/1000)
                        if last_feed_delta>= cat['feed_delay']:
                            # cat['feed_quota']=cat['feed_quota']-1
                            cat['feed_portion_timestamp']=timestamp
                            self.feed()
                            log=log+("Feeding next portion ({:0.2f}g left)".format(cat['feed_quota']))
                            # self.annotation_event(timestamp, "Feeding ({} left)".format(cat['feed_quota']))

                        else:
                            log=log+("Next portion in {} seconds. ({:0.2f}g left)".format(cat['feed_delay']-last_feed_delta, cat['feed_quota']))

                    else:
                        # next_portion= int (cat['feed_rate'] - ((timestamp-cat['feed_quota_timestamp'])/(60*1000)))
                        log=log+("Feed quota empty ({:0.2f}g)".format(cat['feed_quota']))

            print(log)

    def housekeeping(self,force=False):
        """regular saves and batched writing"""

        if force or len(self.points_batch)>10000:
            if self.points_batch:
                # print("Writing to influxdb, processed up to: ", time.ctime(self.db_timestamp/1000))
                self.client.write_points(points=self.points_batch, time_precision="ms")
                self.points_batch=[]

            self.save_state()


    def analyse_measurement(self, timestamp, measurement, scale):
        '''analyse one measurement and store results (time in mS)'''

        self.state['db_timestamp']=timestamp

        self.scale[scale].measurement(timestamp,measurement)

        # store all calculated weights (for analyses and debugging with grafana)
        self.points_batch.append({
            "measurement": "weights",
            "time": timestamp,
            "tags":{
                "scale": scale
            },
            "fields":{
                        'weight': self.scale[scale].calibrated_weight(self.scale[scale].offset(measurement))
                    }
        })

        self.points_batch.append({
            "measurement": "stable_count",
            "time": timestamp,
            "tags":{
                "scale": scale
            },
            "fields":{
                        'stable_count': self.scale[scale].state['stable_count']
                    }
        })

        self.housekeeping()

    def analyse_all(self, reanalyse_days=None):
        '''analyse all existing measurements, in a resumable way.'''
        analysed_measurement_names=["events", "weights", "cats", "cats_debug", "annotations",  "stable_count", "food" ]
        if not self.state['db_timestamp']:
            #drop and recalculate everything
            print("Deleting all analysed data")
            for analysed_measurement_name in analysed_measurement_names:
                self.client.query("drop measurement {}".format(analysed_measurement_name))

        elif reanalyse_days!=None:
            print("Deleting last {} days of analysed data".format(reanalyse_days))
            self.state['db_timestamp']=int((time.time()-(reanalyse_days*24*3600))*1000) # mS
            for analysed_measurement_name in analysed_measurement_names:
                self.client.query("delete from  {} WHERE time > {}".format(analysed_measurement_name, self.state['db_timestamp']*1000000), epoch="ms")


        print("Resuming from: ", time.ctime(self.state['db_timestamp']/1000))

        for result in self.client.query("select * from raw_sensors where time>"+str(self.state['db_timestamp']*1000000), database="meowton", stream=True, chunked=True, chunk_size=10000, epoch='ms'):
            for point in result.get_points():


                if 'scale' in point and point['scale']:
                    scale=point['scale']
                else:
                    scale='cat'


                if scale=='cat':
                    measurement=[
                        point['sensor0'],
                        point['sensor1'],
                        point['sensor2'],
                        point['sensor3'],
                    ]
                else:
                    measurement=[
                        point['sensor0'],
                    ]

                self.analyse_measurement(point['time'], measurement, scale)



        #flush/save last stuff
        self.housekeeping(force=True)

        print("Analyses complete, waiting for new measurement")
        self.realtime=True
