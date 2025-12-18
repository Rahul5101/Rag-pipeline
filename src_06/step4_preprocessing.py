# # --- Imports ---
# from pymilvus import connections, Collection, utility
# from langchain_core.documents import Document
# from src_06.step5_prompts import prompt
# # from src.step_6_reranking import rerank_with_encoder
# from src_06.step7_rerankers import rerank_with_google
# import gc
# import os
# import json
# import time
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from milvus_05.config import DB
# from milvus_05.milvus_db import vector_search
# # from url_integration.gcs_url import generate_signed_url
# import re

# from vertexai.generative_models import GenerativeModel, Part, SafetySetting
# from src_06.llm_config import safety_settings, GENERATION_CONFIG
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.getcwd(),"service-account.json")

# embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# # --- Adjusted process_file ---
# def process_file(query, embedding_model):
#     try:
#         # Step 1: Embed query
#         query_vector = embedding_model.embed_query(query)

#         # Step 2: Search Milvus
#         results = vector_search(
#             collection_name=DB.milvus_collection_name,
#             partition_name=DB.default_partition,
#             query_vectors=query_vector,
#             num_results=30
#         )
#         hits = results[0] if results else []

#         docs, meta_data = [], []

#         for hit in hits:
#             entity = hit["entity"]
#             page = entity.get("page", 0)
#             source = entity.get("source", "Unknown").strip()
#             score = hit.get("distance", None)

#             # Remove everything after the last underscore
#             # if "_" in source:
#             #     source = source.rsplit("_", 1)[0].strip()
#             # else:
#             #     source = source.strip()

#             # # Make short URL placeholder
#             # encoded_source = source.replace(" ", "%20")
#             # temp_url = f"https://storage.cloud.google.com/km-navy-data/DOPT/{encoded_source}.pdf"
#             # signed_url = generate_signed_url(gcs_url=temp_url)
#             # signed_url_with_page = f"{signed_url}#page={page}"

#             doc = Document(
#                 page_content=entity["text"],
#                 metadata={
#                     "page": page,
#                     "source": source,
#                     "score": score,
#                     # "signed_url": signed_url_with_page
#                 }
#             )
#             docs.append(doc)
#             meta_data.append(doc.metadata)

#         # Step 3: Re-rank top docs
#         t1 = time.time()
#         project_id = "km-income-tax"
#         docs = rerank_with_google(query, docs, project_id)[:10]
#         print("Re Ranking Time: ",time.time()-t1)

#         # Step 4: Build context with metadata hints
#         context_chunks = []
#         for doc in docs:
#             md = doc.metadata
#             meta_line = f"[Meta: source={md['source']}, page={md['page']}]"
#             context_chunks.append(f"{doc.page_content}-->{meta_line}\n\n")

#         context = "\n\n".join(context_chunks)

#         # Step 5: LLM call
#         # input_payload = {"question": query, "context": context}
#         # t1 = time.time()
#         # response = (prompt | llm | parser).invoke(input_payload)
#         # print("LLM response time:", time.time() - t1)


#         x1 = time.time()
#         formated_prompt = prompt.format(context=context, question=query)
#         model = GenerativeModel(
#             "gemini-2.5-flash",
#         )
#         result_new = model.generate_content(
#                 formated_prompt,
#                 generation_config=GENERATION_CONFIG,
#                 safety_settings=safety_settings,
#                 # stream=True,
#             )

#         print("result new: ",result_new)
#         print("vertex ai response time: ",time.time()-x1)


#         response = result_new.candidates[0].content.parts[0].text

#         print("llm response : ",response)

#         del docs, context
#         gc.collect()

#         return {
#             "query": query,
#             "response": response,
#             "meta_data": meta_data
#         }

#     except Exception as e:
#         print(f"Error processing '{query}': {e}")
#         return None








from pymilvus import connections, Collection, utility
from langchain_core.documents import Document
from src_06.step5_prompts import prompt
from src_06.step7_rerankers import rerank_with_google
import gc
import os
import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from milvus_05.config import DB
from milvus_05.milvus_db import vector_search
import re
from urllib.parse import quote

from vertexai.generative_models import GenerativeModel
from src_06.llm_config import safety_settings, GENERATION_CONFIG
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.getcwd(),"service-account.json")
embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
from url_integration_09.gcs_url import generate_signed_url
from src_06.utils import load_config
config = load_config()
BASE_URL = config["src"]["preprocessing"]["base_url"]
service_account = config["credentials"]["service_account_path"]
service_account_path = os.path.abspath(service_account)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
projectId = config["credentials"]["project_id"]
model_name = config["llm"]["google"]["model_name"]
RELATIVE_PDF_PATH= config["src"]["preprocessing"]["relative_pdf_path"]
num_result = config["src"]["preprocessing"]["num_result"]

def generate_source_url(source_filename: str, page: int) -> str:
    """
    Generates a URL based on the environment:
    1. Local URI (file:///) for development.
    2. Public GCS HTTPS URL for web deployment.
    """
   
    source_filename = source_filename.split('_')[0].strip()
    clean_filename = f"{source_filename}.pdf"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_pdf_folder = os.path.join(script_dir, RELATIVE_PDF_PATH)
    local_path = os.path.join(absolute_pdf_folder, clean_filename)
    uri_path_slashed = local_path.replace("\\", "/")
    final_path = quote(uri_path_slashed, safe="/:")
    return f"{BASE_URL}{final_path}#page={page}"  

    
def process_file(query, embedding_model,chat_history):
    try:
        # ... (Step 1: Embed query) ...
        query_vector = embedding_model.embed_query(query)

        # Step 2: Search Milvus
        results = vector_search(
            collection_name=DB.milvus_collection_name,
            partition_name=DB.default_partition,
            query_vectors=query_vector,
            num_results=num_result
        )
        hits = results[0] if results else []

        docs, meta_data = [], []

        for hit in hits:
            entity = hit["entity"]
            page = entity.get("page", '')
            source = entity.get("source", "Unknown").strip()
            url = entity.get("url",None)
            score = hit.get("distance", None)

            if url == '':
            
                signed_url_with_page = generate_source_url(source_filename=source, page=page)
            


                doc = Document(
                    page_content=entity["content"],
                    metadata={
                        "page": page,
                        "source": source,
                        "score": score,
                        "url": signed_url_with_page # Storing the generated URL
                    }
                )
                docs.append(doc)
                meta_data.append({
                    "source": source,
                    "url": signed_url_with_page,
                    "page": page,
                    "score": score
                })

            doc = Document(
                page_content=entity["content"],
                metadata={
                    "page": page,
                    "source": source,
                    "score": score,
                    "url": url # Storing the generated URL
                }
            )
            docs.append(doc)
            # Storing full metadata for final output
            meta_data.append({
                "source": source,
                "url": url,
                "page": page,
                "score": score
            })


        t1 = time.time()
        project_id = projectId
        docs = rerank_with_google(query, docs, project_id)[:10]
        print("Re Ranking Time: ",time.time()-t1)

        # Step 4: Build context with metadata hints
        context_chunks = []
        for doc in docs:
            md = doc.metadata
            # Include the generated URL in the context for the LLM to use
            meta_line = f"[Meta: source={md['source']}, page={md['page']}, url={md['url']}]"
            context_chunks.append(f"{doc.page_content}-->{meta_line}\n\n")

        context = "\n\n".join(context_chunks)

        x1 = time.time()
        formated_prompt = prompt.format(context=context, question=query,chat_history=chat_history)
        model = GenerativeModel(
            model_name,
        )
        result_new = model.generate_content(
                formated_prompt,
                generation_config=GENERATION_CONFIG,
                safety_settings=safety_settings,
            )

        # print("result new: ",result_new)
        print("vertex ai response time: ",time.time()-x1)

        response = result_new.candidates[0].content.parts[0].text

        # print("llm response : ",response)

        del docs, context
        gc.collect()

        return {
            "query": query,
            "response": response,
            "meta_data": meta_data # This list now contains the generated URLs
        }

    except Exception as e:
        print(f"Error processing '{query}': {e}")
        return None