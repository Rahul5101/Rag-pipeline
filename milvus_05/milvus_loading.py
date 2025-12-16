from milvus_05.factory_client import MilvusDB
from milvus_05.config import DB
from pymilvus import connections, Collection
import os
from dotenv import load_dotenv
from src_06.utils import load_config
config = load_config()
load_dotenv()
MILVUS_HOST = config["milvus"]["host"]
MILVUS_PORT = config["milvus"]["port"]


def loading_milvus():
    try:
        # Try to connect to Milvus
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        print("✅ Connected to Milvus!")
        collection = Collection(name=DB.milvus_collection_name)
        collection.load()
        print("Collection loaded")
    except Exception as e:
        # If connection fails, initialize and set up
        print("⚠️ Milvus connection failed, initializing database...")
        milvus_db = MilvusDB()
        milvus_client = milvus_db.load_db()
        milvus_db.create_partition_if_not_exists(
            collection_name=DB.milvus_collection_name,
            partition_name=DB.default_partition
        )