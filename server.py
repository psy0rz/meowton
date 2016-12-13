#!/usr/bin/env python3


# import beaker.middleware
import bottle
import re
import traceback
# import json
import sys
import os.path
import time


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
            csv=""
            for measurement in measurements:
                csv=csv+str(int(time.time()))+";"
                for sensor in measurement:
                    csv=csv+(str(sensor)+";")
                csv=csv+"\n"

            with open('measurements.csv','a') as fh:
                fh.write(csv)



    except Exception as e:
        print("Error: "+str(e)+"\n")
        print(bottle.request.body.getvalue())


application=bottle.default_app()

#standalone/debug mode:
if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(reloader=True, app=application, host='0.0.0.0', port=8080)
