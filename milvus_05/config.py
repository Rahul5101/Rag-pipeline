from pymilvus import connections, utility
from dotenv import load_dotenv
import os
from src_06.utils import load_config
config = load_config()
load_dotenv()
MILVUS_HOST = config["milvus"]["host"]
MILVUS_PORT = config["milvus"]["port"]
collection_name = config["milvus"]["collection_name"]
partition_name = config["milvus"]["partition_name"]
model_dim = config["milvus"]["model_dim"]

class DB:
    """
    Configuration class for Milvus Database.
    Stores collection name, embedding dimensions, and other DB params.
    """

    # Default collection name (can be overridden in scripts)
    milvus_collection_name: str = collection_name

    # Embedding dimensions (will be set dynamically after reading FAISS)
    model_dimensions: int = model_dim

    # Local Milvus connection parameters
    host: str = MILVUS_HOST
    port: str = MILVUS_PORT
    user: str = "root"
    password: str = "Milvus"

    # Default partition
    default_partition: str = partition_name


# Connect to Milvus
connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

print("✅ Connected to Milvus!")

# Check collections
print("Available collections:", utility.list_collections())


print("Current DB: ",DB.milvus_collection_name)