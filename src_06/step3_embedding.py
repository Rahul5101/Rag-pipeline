from langchain_community.vectorstores import Milvus
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Initialize embeddings
# embedding_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# Store in Milvus
def embedding_creation(documents):
    vectorstore = Milvus.from_documents(
        documents,
        embedding=embedding_model,
        connection_args={"host": "localhost", "port": "19530"},
        # collection_name="KM_Navy_Update"
        collection_name="income_tax_demo"
    )


    return vectorstore
