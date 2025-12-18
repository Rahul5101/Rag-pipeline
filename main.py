from fastapi import FastAPI,Query, HTTPException
from pydantic import BaseModel
import asyncio
import time
import os
from fastapi.responses import JSONResponse,FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from fastapi import Header
from urllib.parse import unquote,quote
from contextlib import asynccontextmanager
from src_06.step6_llm_loaders import main
from milvus_05.milvus_loading import loading_milvus
# from multilingual_pipeline.language_detector import detect_language
# from multilingual_pipeline.conversion import output_converison,translation

BASE_DIR = os.getcwd()
# app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Server starting up...")
    try:
        await run_in_threadpool(loading_milvus)
    except:
        print("Milvus loading failed during startup.")
    yield

app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://km-income-tax-dot-knowledge-minor.el.r.appspot.com/",
    "*",  # Use "*" to allow all origins (not recommended in production)
]
# Add CORS middleware to your app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # List of allowed origins
    allow_credentials=True,           # Allow cookies and auth headers
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)


# Request model: user sends a question
class QuestionRequest(BaseModel):
    question: str
    session_id: str
# # Response model: we respond with JSON
class AnswerResponse(BaseModel):
    answer: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/open-pdf")
async def open_pdf_endpoint(file_path:str=Query(..., description="Encoded absolute file path with optional #page=N anchor.")):
    """
    Reads a local file path sent via a query parameter and streams the PDF 
    file back to the browser via HTTP, bypassing file:// security.
    """
    decoded_path = unquote(file_path)
    # filepath = decoded_path.split("#",1)[0]
    # page_anchor = f"#{filepath[1]}" if len(filepath) > 1 else ""
    clean_path=os.path.normpath(decoded_path)

    # clean_path1 = os.path.basename(clean_path)
    # clean_filepath = quote(clean_path1 + page_anchor, safe="")


    return FileResponse(
        clean_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={quote(os.path.basename(clean_path), safe='')}"
        }
    )

@app.post("/query", response_model=AnswerResponse)
async def answer_question(request: QuestionRequest):
    user_question = request.question
    session_id = request.session_id
    start_time = time.time()

    

    print("translated query: ",user_question)
    
    response_data = await main(query=user_question,session_id=session_id)
    elapsed_time = time.time() - start_time

    print(f"\nTotal time consumed: {elapsed_time:.2f} seconds")

    return JSONResponse(response_data)

# @app.get("/query_get")
# def answer_question_get(question: str = Query(..., description="The user question to be processed by the RAG pipeline.")):
#     """
#     Accepts a user query via a GET request URL parameter and processes it
#     through the RAG pipeline (main function).
#     """
#     user_question = question
#     start_time = time.time()

#     print("translated query: ", user_question)
#     db_load = loading_milvus()

#     try:
#         # Run the asynchronous main function synchronously
#         response_data = asyncio.run(main(query=user_question))
#     except Exception as e:
#         # Handle exceptions gracefully, logging the error
#         print(f"Error processing GET query: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error during RAG processing.")


#     elapsed_time = time.time() - start_time
#     print(f"\nTotal time consumed: {elapsed_time:.2f} seconds")

#     # Return the response data
#     return JSONResponse(content=response_data)