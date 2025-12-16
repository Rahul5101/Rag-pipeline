import fitz  
import io
from PIL import Image
# import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from google import genai
import os
import time
import base64
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from src_06.utils import load_config
config = load_config()
load_dotenv()
model= config["llm"]["google"]["model_name"]
chunk_size = config["data_ingestion"]["ocr"]["chunk_size"] 
input_folder = config["data_ingestion"]["ocr"]["input_folder"] 
output_folder = config["data_ingestion"]["ocr"]["output_folder"] 

API_KEY = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview",google_api_key=API_KEY)

def pdf_to_images(pdf_path):
    pdf_document = fitz.open(pdf_path)
    images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    return images


def extract_text_with_gemini(images, output_base_path, base_name, chunk_size=chunk_size):
    total_pages = len(images)
    for chunk_start in range(0, total_pages, chunk_size):
        chunk_end = min(chunk_start + chunk_size, total_pages)
        output_txt_path = os.path.join(
            output_base_path, f"{base_name}.txt"
        )
        os.makedirs(output_base_path, exist_ok=True)  # ensure subfolder exists

        with open(output_txt_path, "w", encoding="utf-8") as f:
            for i, img in enumerate(images[chunk_start:chunk_end], start=chunk_start+1):
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                time.sleep(2)  # API rate limiting
                prompt = '''
                    Extract each and every content in this image as it is even if some content is repeated.
                    Explain in an understandable way and do explain the mapping if it is needed
                    (which value belongs to which field).
                    if there is handwritten words then extract them in english word precisely.
                    Provide everything in English, if the text
                    is Hindi or some other language then first translate into English.
                    Do not make any assumption in prediction, always try to extract that is present in the image.

                    You are a text extractor from images. Follow these steps carefully:

                    1. First analyze the image and then extract **all visible content exactly as it appears**, even if some content is repeated.  
                    2. If the image contains a **table**, extract it properly and also explain the mapping between rows and columns so that the semantic meaning is not lost.  
                    3. If the image contains **normal text or paragraphs**, extract them exactly as they are without adding or modifying anything.  
                    4. Only explain the mapping for tables.  
                    5. If there are handwritten words, transcribe them accurately into English.   
                    7. Do not add any extra text, introductions, or conclusions before or after the extraction. Only provide the extracted content (and table mapping if applicable).  
                    '''
                
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_str}"},
                        },
                    ]
                )
                response = model.invoke([message])

                page_text = response.content or ""
                f.write(f"\n--- Page {i} ---\n{page_text}\n")
                f.flush()
                print(f"[INFO] Saved Page {i} → {output_txt_path}")

        print(f"[CHUNK DONE] Pages {chunk_start+1}-{chunk_end} saved in {output_txt_path}")

    return True


def process_file(pdf_path, input_folder, output_folder):
    if not pdf_path.lower().endswith(".pdf"):
        return f"Skipping {pdf_path} (not a PDF)."

    rel_path = os.path.relpath(pdf_path, input_folder)  # relative subfolder/file.pdf
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    output_subfolder = os.path.join(output_folder, os.path.dirname(rel_path))

    t0 = time.time()
    try:
        images = pdf_to_images(pdf_path)
        extract_text_with_gemini(images, output_subfolder, base_name, chunk_size=250)
        elapsed = time.time() - t0
        return f"{pdf_path} processed in {elapsed:.2f} sec → saved in {output_subfolder}"
    except Exception as e:
        return f":x: Error processing {pdf_path}: {str(e)}"


def main():
    input_folder = input_folder      # root folder with subfolders
    output_folder = output_folder  # root output folder
    os.makedirs(output_folder, exist_ok=True)

    # Recursively collect all PDFs
    pdf_files = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))

    start = time.time()
    # Run with 1 worker for safety (adjust if needed)
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(process_file, pdf, input_folder, output_folder) for pdf in pdf_files]
        for future in as_completed(futures):
            print(future.result())
    print(f"\n:rocket: All done in {time.time() - start:.2f} sec")

if __name__ == "__main__":
    main()

