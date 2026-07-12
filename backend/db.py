import pymongo
from django.conf import settings

# MongoDB Connection Variable
MONGO_URI = getattr(settings, 'MONGO_URI', 'mongodb://localhost:27017/')

client = pymongo.MongoClient(MONGO_URI)
db = client['pharmacy_db']

# Collections
users_collection = db['Users']
categories_collection = db['Categories']
medicines_collection = db['Medicines']
cart_collection = db['Cart']
orders_collection = db['Orders']

# Indexes for faster search
users_collection.create_index([("email", pymongo.ASCENDING)], unique=True)
categories_collection.create_index([("categoryName", pymongo.ASCENDING)], unique=True)
medicines_collection.create_index([("medicineName", pymongo.ASCENDING)])
medicines_collection.create_index([("category", pymongo.ASCENDING)])
