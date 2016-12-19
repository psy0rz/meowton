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



def doc_generator():
    prev_timestamp=0
    nr=0
    with open('measurements.csv','r') as fh:
        for line in fh:
            # print(line)
            (timestamp, *sensor_strs)=line.rstrip(";\n").split(";")

            if timestamp != prev_timestamp:
                nr=0
                prev_timestamp=timestamp

            #make ints
            sensors=[]
            for sensor_str in sensor_strs:
                sensors.append(int(sensor_str))

            doc={
                'timestamp':    timestamp,
                'nr':           nr,
                'sensors':      sensors
            }
            nr=nr+1
            yield(doc)

db.measurements.insert_many(doc_generator())
