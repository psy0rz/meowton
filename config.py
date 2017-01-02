import pymongo


mongodb_connection = pymongo.mongo_client.MongoClient()
db = mongodb_connection['meowton']
