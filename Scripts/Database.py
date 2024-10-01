from pymongo import MongoClient

from Config import DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_USER

client = MongoClient(F'mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}')

database = client.get_database('MCCAG')

cache_collection = database.get_collection('Cache')
image_collection = database.get_collection('Image')
