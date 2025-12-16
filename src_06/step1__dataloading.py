# import re
# import os
# import json
# from langchain_core.documents import Document

# from langchain_community.document_loaders import PyPDFLoader

# def load_txt(file_path: str):
#     """
#     read a json metadata file and convert each entry to a langchain document
#     the json is expected to have the list of records:
#     id, page_no, case_name, section, citation, case_body
#     """

#     docs = [] 
#     filename = os.path.basename(file_path)
#     source_name = os.path.splitext(filename)[0]

#     with open(file_path, "r", encoding="utf-8") as f:
#         data = json.load(f)
    
#     for entry in data:
#         page_content = entry.get("text", "").strip()
        
#         metadata = {
#             "id": entry.get("id"),
#             "page": entry.get("page"),
#             "source": source_name   
#         }
#         doc = Document(
#             page_content=page_content,
#             metadata=metadata
#         )
#         docs.append(doc)
#     return docs


# # if __name__ == "__main__":
# #     path = r"D:\valiance_sol\01_project\clean_04\Digest Book income tax Case law 2024 (1)_1-101.json"
# #     documents = load_txt(path)

# #     print(f"Loaded {len(documents)} LangChain documents.")
# #     print(documents[4])

















