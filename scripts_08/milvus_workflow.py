from milvus_05.factory_client import MilvusDB
from milvus_05.config import DB
from milvus_05.milvus_db import insert_documents_in_milvus

from src_06.step2_chunking import load_txt

milvus_db = MilvusDB()
milvus_client = milvus_db.load_db()
milvus_db.create_partition_if_not_exists(collection_name=DB.milvus_collection_name,partition_name=DB.default_partition)


import os
from pathlib import Path

def process_folder(root_folder: str):
    total_vectors = 0
    filewise_stats = {}

    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(subdir, file)
                print(f"\n📂 Processing file: {file_path}")

                # Load + chunk
                docs = load_txt(file_path=file_path)
                print(f"   ➝ Loaded {len(docs)} chunks from {file}")

                # Insert into Milvus
                inserted_count, skipped_count = insert_documents_in_milvus(docs=docs)

                # Track stats
                filewise_stats[file_path] = {
                    "inserted": inserted_count,
                    "skipped": skipped_count
                }
                total_vectors += inserted_count

                print(f"   ✅ Inserted: {inserted_count}, Skipped: {skipped_count}")

    # Final summary
    print("\n📊 --- Insertion Summary ---")
    for fpath, stats in filewise_stats.items():
        print(f"{fpath} ➝ Inserted: {stats['inserted']}, Skipped: {stats['skipped']}")
    print(f"\n🎯 Total vectors inserted across all files: {total_vectors}")



# --- Run on your folder ---
if __name__ == "__main__":
    process_folder(r"D:\valiance_sol\01_project\clean_04\final_cleaned_file")
