import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from milvus_05.factory_client import MilvusDB
from milvus_05.config import DB
from milvus_05.milvus_db import insert_documents_in_milvus
from src_06.step2_chunking import chunk_documents


from src_06.step2_chunking import load_txt   # Import the module directly

milvus_db = MilvusDB()
milvus_client = milvus_db.load_db()

file_path = r"D:\valiance_sol\01_project\clean_04\Digest Book income tax Case law 2024 (1)_1-101.json"
docs = load_txt(file_path=file_path)
chunked_docs = chunk_documents(docs=docs)

insert_documents_in_milvus(docs=docs)
