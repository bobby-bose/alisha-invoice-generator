from pymongo import MongoClient
from datetime import datetime

# 🔹 MongoDB connection details
MONGO_URL = "mongodb+srv://admin:admin@cluster.rnhig2f.mongodb.net/?retryWrites=true&w=majority&appName=cluster"
DB_NAME = "mamshi"       # you can rename this to whatever DB you want
COLLECTION_NAME = "report_two"

def push_to_mongo(data: dict):
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Add timestamps
        data["date_created"] = datetime.now().strftime("%Y-%m-%d")
        data["time_created"] = datetime.now().strftime("%H:%M:%S")

        collection.insert_one(data)
        print("✅ Data inserted into MongoDB:", data)

    except Exception as e:
        print("❌ Error inserting into MongoDB:", str(e))
