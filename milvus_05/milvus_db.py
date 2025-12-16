from milvus_05.config import DB
import os
from milvus_05.factory_client import MilvusDB
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from uuid import uuid4
from dotenv import load_dotenv
load_dotenv()
from pymilvus import Collection
from src_06.utils import load_config
config = load_config()
# batch_size = 10  # adjust based on memory and Milvus performance
model= config["llm"]["google"]["model_name"]
batch_size = config["milvus"]["batch_size"]
partition_name = config["milvus"]["partition_name"]
embedding_model = GoogleGenerativeAIEmbeddings(model=model)
milvus_db = MilvusDB()
milvus_client = milvus_db.load_db()

milvus_db.create_milvus_collection_if_not_exists()

def insert_documents_in_milvus(docs, partition_name=partition_name, batch_size=batch_size):
    """
    Inserts LangChain Document objects into Milvus in batches,
    skipping duplicates using a Python set for fast lookups.
    """
    # 1. Load existing texts from Milvus once
    existing_texts = get_existing_texts(partition_name)
    print(f"🔍 Found {len(existing_texts)} existing records in Milvus")

    batch = []
    total_docs = 0
    skipped = 0

    for doc in docs:
        content = doc.page_content.strip()
        page = doc.metadata.get("page", '')
        source = doc.metadata.get("source", "unknown")
        url = doc.metadata.get("url",None)

        # Skip if text already exists
        if content in existing_texts:
            skipped += 1
            continue  

        # Generate embedding
        embedding = embedding_model.embed_query(content)

        # Prepare Milvus record
        record = {
            "uuid_id": str(uuid4()),
            "content": content,
            "page": page,
            "source": source,
            "url": url,
            "vector": embedding
        }
        batch.append(record)
        existing_texts.add(content)  # update local cache
        total_docs += 1

        print("Total Docs Count: ",total_docs)

        # Insert batch when batch_size is reached
        if len(batch) >= batch_size:
            insert_partition_data_in_collection(partition_name, batch)
            print(f"✅ Inserted {len(batch)} new docs (Total so far: {total_docs})")
            batch = []

    # Insert any remaining records
    if batch:
        insert_partition_data_in_collection(partition_name, batch)
        print(f"✅ Inserted final {len(batch)} docs (Total: {total_docs})")

    print(f"🎯 Finished: Inserted {total_docs} new docs, Skipped {skipped} duplicates.")

    return total_docs, skipped 


def get_existing_texts(partition_name):
    """
    Fetches all existing texts from a Milvus partition and returns a Python set.
    """
    collection = Collection(DB.milvus_collection_name)
    collection.load()

    existing_texts = set()
    offset = 0
    limit = 2000  # fetch in chunks to avoid memory issues

    while True:
        res = collection.query(
            expr="",
            output_fields=["content"],
            partition_names=[partition_name],
            offset=offset,
            limit=limit
        )
        if not res:
            break
        for r in res:
            existing_texts.add(r["content"])
        offset += limit

    return existing_texts


def insert_partition_data_in_collection(partition_name, data):
    """Inserts data into a partition within the all_table_data collection"""
    collection_name = DB.milvus_collection_name
    # Ensure the collection exists before inserting data
    if not milvus_client.has_collection(collection_name):
        print(f"Collection '{collection_name}' does not exist. Creating it first.")
        milvus_client.create_milvus_collection_if_not_exists(collection_name)

    res = milvus_db.insert_data(partition_name=partition_name, data=data)
    return res




def vector_search(collection_name, partition_name ,query_vectors, num_results):
    
    res = milvus_client.search(
        collection_name=collection_name,  # target collection
        partition_names=[partition_name],
        data=[query_vectors],  # query vectors
        limit=num_results,  # number of returned entities
        output_fields=["content", "page", "source","url"],# specifies fields to be returned
    )
    return res


def retrieve_all_collections():
    collections = milvus_client.list_collections()
    return collections

def unique_results(res):
    seen_texts = set()
    unique_results = []  # To eliminate duplicate paragraphs with same text
    for result in res[0]:
        if result['entity']['content'] not in seen_texts:
            seen_texts.add(result['entity']['content'])
            unique_results.append(result)
    return unique_results

def retrieve_collection_schema(collection_name):
    try:
        # Retrieve collection schema
        schema = milvus_client.describe_collection(collection_name)

        # Print schema details
        print(f"Collection: {schema}")

    except Exception as e:
        print(f"Error retrieving schema for collection '{collection_name}': {e}")


def retrieve_all_data_in_schema(collection_name):
    return milvus_client.get_collection_stats(collection_name=collection_name)



def vector_search_truths(partition_names, query_embeddings):
    """
    Retrieves data from multiple partitions and returns table name and row data.
    Args:
        collection_name (str): Name of the collection
        partition_names (list): List of partition names
        query_embeddings: Vector embeddings to search with
    Returns:
        list: List of dictionaries containing table_name and row_data
    """
    try:
        collection_name = DB.milvus_collection_name
        existing_partitions = [p for p in partition_names if milvus_db.model.has_partition(
            collection_name=collection_name,
            partition_name=p
        )]
        if not existing_partitions:
            return []
        collection_name = DB.milvus_collection_name
        results = milvus_db.model.search(
            collection_name=collection_name,
            data=query_embeddings,
            limit=40,  # Get 2 results per partition
            output_fields=["content"],
            # specifies fields to be returned
            partition_names=existing_partitions,  # Search one partition at a time
            search_params={
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
        )
        return results

    except Exception as e:
        print(f"Error retrieving partition data: {e}")
        return []

def delete_partition(collection_name, partition_name):
    milvus_db.drop_partition(collection_name=collection_name, partition_name=partition_name)
    print(f"Deleted partition {partition_name} from collection {collection_name}")





