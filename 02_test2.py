# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from vertexai.generative_models import GenerativeModel
# from langchain.memory import VectorStoreRetrieverMemory
# from langchain.chains import ConversationChain
# from langchain.prompts import PromptTemplate
# from langchain.vectorstores import Milvus
# from dotenv import load_dotenv
# load_dotenv()
# import os
# from src_06.utils import load_config
# config = load_config()
# from milvus import default_server
# default_server.start()
# model_name = config["llm"]["google"]["model_name"]
# service_account = config["credentials"]["service_account_path"]
# service_account_path = os.path.abspath(service_account)
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
# embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
# model = GenerativeModel(
#             model_name,
#         )

# vectordb = Milvus.from_documents(
#    {},
#    embedding_model,
#    connection_args={"host": "localhost", "port": 
#    default_server.listen_port})
# retriever = Milvus.as_retriever(vectordb, search_kwargs=dict(k=1))
# memory = VectorStoreRetrieverMemory(retriever=retriever)
# about_me = [
#    {"input": "My favorite snack is chocolate",
#     "output": "Nice"},
#    {"input": "My favorite sport is swimming",
#     "output": "Cool"},
#    {"input": "My favorite beer is Guinness",
#     "output": "Great"},
#    {"input": "My favorite dessert is cheesecake",
#     "output": "Good to know"},
#    {"input": "My favorite musician is Taylor Swift",
#     "output": "Same"}
# ]
# for example in about_me:
#    memory.save_context({"input": example["input"]}, {"output": example["output"]})


#  # Can be any valid LLM
# _DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.


# Relevant pieces of previous conversation:
# {history}


# (You do not need to use these pieces of information if not relevant)


# Current conversation:
# Human: {input}
# AI:"""
# PROMPT = PromptTemplate(
#    input_variables=["history", "input"], template=_DEFAULT_TEMPLATE
# )
# conversation_with_summary = ConversationChain(
#    llm=model,
#    prompt=PROMPT,
#    memory=memory,
#    verbose=True
# )
# conversation_with_summary.predict(input="Hi, my name is Gary, what's up?")



from dotenv import load_dotenv
import os

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from langchain_community.vectorstores import Milvus

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from milvus import default_server
from src_06.utils import load_config

load_dotenv()
config = load_config()

service_account = os.path.abspath(
    config["credentials"]["service_account_path"]
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account
default_server.start()
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)
vectordb = Milvus.from_texts(
    texts=[],
    embedding=embedding_model,
    connection_args={
        "host": "localhost",
        "port": default_server.listen_port
    }
)
about_me = [
   {"input": "My favorite snack is chocolate",
    "output": "Nice"},
   {"input": "My favorite sport is swimming",
    "output": "Cool"},
   {"input": "My favorite beer is Guinness",
    "output": "Great"},
   {"input": "My favorite dessert is cheesecake",
    "output": "Good to know"},
   {"input": "My favorite musician is Taylor Swift",
    "output": "Same"}
]
texts = [
    f"User said: {item['input']} | Assistant replied: {item['output']}"
    for item in about_me
]
vectordb.add_texts(texts)
retriever = vectordb.as_retriever(search_kwargs={"k": 2})
llm = ChatGoogleGenerativeAI(
    model=config["llm"]["google"]["model_name"],
    temperature=0.3
)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly AI assistant."),
    ("human", "{input}")
])
chain = prompt | llm
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]
conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)
response = conversation.invoke(
    {"input": "Hi, my name is Gary, what's up?"},
    config={"configurable": {"session_id": "gary-1"}}
)

print(response.content)

