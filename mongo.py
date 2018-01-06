import pymongo
from pymongo import MongoClient
import pprint
import os

client = MongoClient('localhost', 27017)
db = client.openstreetmap
collection = db.livermore

# Print file sizes

print('\nSize of OSM file is {} MB\n'.format(os.path.getsize('livermore_ca_overpassAPI.osm')/1.0e6))

print('Size of the .json file is {} MB\n'.format(os.path.getsize('livermore_ca_overpassAPI.osm.json')/1.0e6))

# Number of documents in our collection
print('The number of documents in our collection: {}\n'.format(collection.find().count()))

# Number of Users in Collection
print('The number of unique users in our collection: {}\n'.format(len(collection.distinct('created.user'))))

# Number of ways and nodes
print('The number of "node\'s" and "way\'s" in the collection.')
for document in collection.aggregate([{'$group': {'_id': '$type', 'count': {'$sum': 1}}}]):
    pprint.pprint(document)
