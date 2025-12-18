from milvus_05.factory_client import MilvusDB
from milvus_05.config import DB
from pymilvus import connections, Collection, utility
import os
from dotenv import load_dotenv
from src_06.utils import load_config
config = load_config()
load_dotenv()
MILVUS_HOST = os.getenv("MILVUS_HOST")
MILVUS_PORT = os.getenv("MILVUS_PORT")


def loading_milvus():
    try:
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        print("✅ Connected to Milvus!")
        
        # Check if collection exists before loading
        if utility.has_collection(DB.milvus_collection_name):
            collection = Collection(name=DB.milvus_collection_name)
            collection.load()
            print(f"📦 Collection '{DB.milvus_collection_name}' loaded into RAM")
        else:
            print(f"⚠️ Collection {DB.milvus_collection_name} not found. Initializing...")
            milvus_db = MilvusDB()
            # ... rest of your setup logic
    except Exception as e:
        print(f"❌ Milvus Setup Error: {e}")