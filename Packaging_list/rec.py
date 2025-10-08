# fetch_mongo_to_json_func.py
from pymongo import MongoClient
from bson import ObjectId, json_util
import os

# ---------------- MongoDB Config ----------------
MONGO_URL = "mongodb+srv://username:password@cluster.rnhig2f.mongodb.net/?retryWrites=true&w=majority&appName=cluster"
DB_NAME = "mamshi"
COLLECTION_NAME = "report_two"

# ---------------- Function to fetch and save ----------------
def fetch_and_save_document(document_id: str):
    """
    Fetch a MongoDB document by ID and save it as a JSON file.
    
    Args:
        document_id (str): MongoDB ObjectId as string.
    """
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        doc = collection.find_one({"_id": ObjectId(document_id)})
        if not doc:
            print(f"No document found with ID: {document_id}")
            return

        # Path to save JSON
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "data.json")

        # Save as JSON
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_util.dumps(doc, indent=4))

        print(f"✅ Document saved to {json_path}")

    except Exception as e:
        print("❌ Error:", str(e))


