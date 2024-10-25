from pymongo import MongoClient
import os
import certifi

try:
    client = MongoClient(os.getenv('MONGO_URI'), tlsCAFile=certifi.where())
    db = client['users']
    print("MongoDB connected successfully")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")


def get_patient_collection():
    return db['patient']


def get_doctor_collection():
    return db['doctor']
