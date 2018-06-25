# import pymongo
#
#
# mongodb_connection = pymongo.mongo_client.MongoClient(host='media')
# db = mongodb_connection['meowton']
import influxdb

db = influxdb.InfluxDBClient('localhost', 8086, database="meowton")
db.create_database("meowton")
