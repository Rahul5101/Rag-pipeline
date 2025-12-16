
import re
import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
from src_06.utils import load_config
config = load_config()

class fileloader:
    def __init__(self,filepath:str):
        self.filepath = filepath
        self.chunk_size = config["src"]["chunking"]["chunk_size"]
        self.chunk_overlap = config["src"]["chunking"]["chunk_overlap"]
        filename = os.path.basename(filepath)
        self.docs = [] 
        if filename.lower().endswith(".txt"):
            self.docs = self.load_txt(self.filepath)
        elif filename.lower().endswith(".json"):
            self.docs = self.load_json(self.filepath)
        else:
            print(f"Skipping unsupported file type: {filepath}")
        


    
    def load_txt(self,file_path: str):
        docs = []
        filename = os.path.basename(file_path)  # get file name only
        source_name = os.path.splitext(filename)[0]  # remove extension

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue  # skip empty lines

                # Expect format like "Page 1: some text..."
                match = re.match(r"Page\s+(\d+):\s*(.*)", line)
                if match:
                    page_num = int(match.group(1))
                    text = match.group(2).strip()
                    docs.append(Document(
                        page_content=text,
                        metadata={"page": page_num, "source": source_name,"url":""}
                    ))
                else:
                    # fallback if no match (just store raw line)
                    docs.append(Document(
                        page_content=line,
                        metadata={"source": source_name},
                        url = ""
                    ))

        splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        split_docs = splitter.split_documents(docs)
        return split_docs
    def load_json(self,file_path: str ):
        """
        Loads documents from a .json file.
        The JSON file is expected to be a list of dictionaries, where each dictionary
        represents a document (or a chunk that will later be merged/split).

        Args:
            file_path (str): The path to the JSON file.
            content_key (str): The key in the JSON dictionary that holds the main text content.
                            Defaults to "text".
            metadata_keys (List[str]): A list of keys whose values should be added to the
                                    Document's metadata. If None, all other keys are used.

        Returns:
            List[Document]: A list of LangChain Document objects (not yet split).
        """
        docs = []


        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)


        for item in data:     
            page_content = item.get("content")
            if not page_content or not isinstance(page_content, str):
                print(f"Warning: Item skipped due to missing or invalid 'content' in {file_path}")
                continue
            # Initialize metadata
            metadata = {"source": item.get("title"), "url": item.get("url")}
            
            
            
            docs.append(Document(
                page_content=page_content,
                metadata=metadata
            ))
        splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        split_docs = splitter.split_documents(docs)
        return split_docs
