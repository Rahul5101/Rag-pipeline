# --- Imports ---
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
import os
import json
import re
from dotenv import load_dotenv
load_dotenv()
import asyncio
from src_06.step4_preprocessing import process_file
from src_06.utils import load_config
# from multilingual_pipeline.conversion import output_converison
# from url_integration.gcs_url import generate_signed_url
# from src.step_7_utility import extract_markdown_tables
import time
import re
from src_06.step8_utility import escape_inner_quotes,replace_links,safe_json_loads

async def main(query):
    print("Loading embedding model and LLM...")
    config = load_config()
    em_model = config['embedding']['google']['model_name']
    embedding_model = GoogleGenerativeAIEmbeddings(model=em_model)

    tasks = process_file(query=query, embedding_model=embedding_model)
    
    results = [tasks]

    # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&7")
    # print("Result: ",results)
    # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&7")

    per_file_responses = [r for r in results if r]

    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # print("per file response: ",per_file_responses)
    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    # More robust irrelevant response detection
    irrelevant_response_pattern = re.compile(
        r"(does not provide relevant information|answer is not available)", re.IGNORECASE
    )


    # Step 1: Filter irrelevant responses
    all_meta_data = []
    for r in per_file_responses:
        if irrelevant_response_pattern.search(r["response"]):
            continue
        all_meta_data.extend(r["meta_data"])

    # Step 2: Clean file names and deduplicate
    seen_files_pages = set()
    deduped_meta_data = []

    for m in all_meta_data:
        file_name = m.get("source")
        
        # Remove everything after the last underscore
        if "_" in file_name:
            base_file_name = file_name.rsplit("_", 1)[0].strip()
        else:
            base_file_name = file_name.strip()
        
        m["source"] = base_file_name
        
        # Deduplicate by (file_name, page_number)
        file_page = (base_file_name, m.get("page"))
        if file_page not in seen_files_pages:
            deduped_meta_data.append(m)
            seen_files_pages.add(file_page)

    all_meta_data = deduped_meta_data
    # print("all_meta_data::::::::: ",all_meta_data)


    print("\nGenerating final summary...")
    complete_response = "\n\n".join([f"{r['response']}" for r in per_file_responses])

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Complete_res: ",complete_response)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")

    bold_words = list(set(re.findall(r"\*\*(.*?)\*\*", complete_response)))


    # Example LLM output
    raw_text = complete_response
    # print(raw_text)

    html_text = replace_links(raw_text, all_meta_data)
    # print("html_text",html_text)


    clean_output = html_text.strip()
    clean_output = escape_inner_quotes(clean_output)

    # print("Clean output:",(clean_output.strip()))


    # Convert to dict
    # translated_output = json.loads(clean_output)
    translated_output = safe_json_loads(clean_output)

    print("888888888888888888",type(translated_output))
    # print("!!!!!!!!!!!!!!",translated_output.keys())

    explanation_and_summary = f"{translated_output.get('Explanation')}\n\n**Summary:**\n{translated_output.get('Summary')}"

    follow_up_question = translated_output.get('Follow_up')

    table_data = translated_output.get("table_data")


    c1 = time.time()
    print("translation time: ",time.time()-c1)


    output = {
        "bold_words": bold_words,
        "meta_data": all_meta_data,
        "response": explanation_and_summary,
        "follow_up":follow_up_question,
        "table_data": [table_data],
        "ucid": "99_18"
    }
    print("final output", output)

    # print(output)
    return output

