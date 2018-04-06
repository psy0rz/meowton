#!/usr/bin/env python3


# import beaker.middleware
import bottle
import re
import traceback
# import json
import sys
import os.path
import time

# import pymongo
# import bson.objectid


from config import db


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
            timestamp=int(time.time())
            points=[]
            measurement_nr=0
            print(int ((timestamp+measurement_nr*0.1)*1000000000))
            for measurement in measurements:
                points.append(
                    {
                        "measurement": "raw_sensors",
                        "time": int ((timestamp+measurement_nr*0.1)*1000000000),
                        "fields":{
                                    'sensor0': measurement[0],
                                    'sensor1': measurement[1],
                                    'sensor2': measurement[2],
                                    'sensor3': measurement[3]
                                }
                    }
                )
                measurement_nr=measurement_nr+1

            db.write_points(points)

    except Exception as e:
        print("Error: "+str(e)+"\n")
        print(bottle.request.body.getvalue())


application=bottle.default_app()

#standalone/debug mode:
if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(reloader=True, app=application, host='0.0.0.0', port=8080)
