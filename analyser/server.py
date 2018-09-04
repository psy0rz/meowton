#!/usr/bin/env python3

### dependencys in ubuntu:

# sudo apt-get install python3-matplotlib python3-scipy python3-pymongo python3-gdbm python3-influxdb


# import json



import config
import bottle
import argparse
import traceback
import time



from meowton import Meowton



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
            if len(measurements[0])==4:
                #cat scale
                for measurement in measurements:
                    timestamp=current_timestamp+measurement_nr*0.1
                    # store raw data so we can reanalyse if we change our algo.
                    meowton.points_batch.append(
                        {
                            "measurement": "raw_sensors",
                            "time": int(timestamp*1000), # in mS
                            "tags":{
                                "scale": "cat"
                            },
                            "fields":{
                                        'sensor0': measurement[0],
                                        'sensor1': measurement[1],
                                        'sensor2': measurement[2],
                                        'sensor3': measurement[3]
                                    }
                        }
                    )
                    meowton.analyse_measurement(int(timestamp*1000), measurement, "cat") # in mS
                    measurement_nr=measurement_nr+1
            else:
                #food scale
                # print(measurements)
                for measurement in measurements:
                    timestamp=current_timestamp+measurement_nr*0.1
                    meowton.points_batch.append(
                        {
                            "measurement": "raw_sensors",
                            "time": int(timestamp*1000), # in mS
                            "tags":{
                                "scale": "food"
                            },
                            "fields":{
                                        'sensor0': measurement[0],
                                    }
                        }
                    )
                    meowton.analyse_measurement(int(timestamp*1000), measurement, "food") # in mS
                    measurement_nr=measurement_nr+1





    except Exception as e:
        print("Error: "+str(e)+"\n")
        print(bottle.request.body.getvalue())
        traceback.print_exc()


### parse args

parser = argparse.ArgumentParser(description='Meowton v1.0')
parser.add_argument('--reanalyse', help='Reanalyse last X days.', type=int)

#note args is the only global variable we use, since its a global readonly setting anyway
args = parser.parse_args()


# initialize
meowton=Meowton(config.db)

# make sure we're uptodate with the analyser
meowton.analyse_all(args.reanalyse)

# start server
application=bottle.default_app()
bottle.run(quiet=True,reloader=False, app=application, host='0.0.0.0', port=8080)
