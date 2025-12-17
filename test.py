from milvus_05.factory_client import MilvusDB
from milvus_05.config import DB
from milvus_05.milvus_db import insert_documents_in_milvus, vector_search

# from src_06.step2_chunking import load_txt
from src_06.step6_llm_loaders import main
from langchain_google_genai import GoogleGenerativeAIEmbeddings
embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
import asyncio
import time
# from multilingual_pipeline.language_detector import detect_language
# from multilingual_pipeline.conversion import translation

milvus_db = MilvusDB()
milvus_client = milvus_db.load_db()
milvus_db.create_partition_if_not_exists(collection_name=DB.milvus_collection_name,partition_name=DB.default_partition)
start = time.time()

query = "what is the charge of income tax capital?"
# query = "tell me about the  Estimation of Profit in Sahara Land Dealings"
# query = "What were the specific details of the seized material that corroborated the 20% profit margin?"
# query = "tell me about Income tax Q and A-16 Section 54/54F -6 Q51"
print("query: ",query)


session_id="test_session_1"


# print("translated query: ",query)

response = asyncio.run(main(query=query,session_id=session_id))

# print("Response: ",response)

elapsed_time = time.time() - start

print("Total time", elapsed_time)


