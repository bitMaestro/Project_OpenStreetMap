import pymongo
from pymongo import MongoClient
import pprint
import os

client = MongoClient('localhost', 27017)
db = client.openstreetmap
collection = db.livermore

def find_coll(key, value):
    # search for field key value pairs
    global collection
    for document in collection.find({key : value}):
        pprint.pprint(document)

find_coll('amenity', 'ice_cream')