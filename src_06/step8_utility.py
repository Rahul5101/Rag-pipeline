import re

# def extract_markdown_tables(text):
#     """
#     Extracts markdown tables from text and converts them into structured JSON.
#     Returns [] if no tables found.
#     """
#     table_pattern = re.compile(
#         r'((?:\|.*?\|\s*\n)+)',  # Matches Markdown table blocks
#         re.MULTILINE
#     )
#     tables = []

#     for match in table_pattern.findall(text):
#         lines = [line.strip() for line in match.strip().split('\n') if line.strip()]
#         if len(lines) < 2:
#             continue
#         headers = [h.strip() for h in lines[0].split('|')[1:-1]]
#         data_lines = [l for l in lines[2:] if l.strip()]  # Skip header + alignment line

#         rows = []
#         for dl in data_lines:
#             cols = [c.strip() for c in dl.split('|')[1:-1]]
#             rows.append(cols)

#         tables.append({"headers": headers, "rows": rows})

#     return tables



def escape_inner_quotes(text: str) -> str:
    """
    Escapes inner double quotes inside <a ...> and other HTML tags
    so the JSON remains valid.
    """
    # Escape quotes inside any <...> tag attributes
    def replacer(match):
        tag = match.group(0)
        # Escape only attribute quotes, not tag boundary <>
        tag = tag.replace('"', '\\"')
        return tag

    # Apply escaping to all HTML tags
    text = re.sub(r"<[^>]+>", replacer, text)
    return text



def replace_links(text, all_meta_data):
    """
    Replaces markdown-style [Book title, page X](link)
    with <a href="SIGNED_URL" target="_blank">Book title, page X</a>
    using metadata from all_meta_data list.
    """

    # Regex to match patterns like [Seamy book 2024_151-200, page 186](link)
    pattern = r'\[([^\]]+?),\s*page\s*(\d+)\]\(link\)'

    def repl(m):
        book = m.group(1).strip()
        page = m.group(2).strip()
        
        # Remove everything after the last underscore
        if "_" in book:
            book = book.rsplit("_", 1)[0].strip()
        else:
            book = book.strip()

        # Try to find matching metadata entry
        matched_entry = next(
            (item for item in all_meta_data if item["source"].strip() == book and str(item["page"]).strip() == page),
            None
        )

        
        if matched_entry and "signed_url" in matched_entry:
            return f'<a href="{matched_entry["signed_url"]}" target="_blank">{book}, page {page}</a>'
        else:
            # fallback: no match found, keep original text
            return f"{book}, page {page}"

    return re.sub(pattern, repl, text)




import json, re

def safe_json_loads(s):
    if not s:
        return None
    if isinstance(s, dict):
        return s
    if isinstance(s, str):
        s = s.strip()
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            # Try to find the first valid JSON object within the string
            match = re.search(r"\{[\s\S]*\}", s)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
    # If all parsing fails
    print("⚠️ safe_json_loads could not parse input, returning None")
    return None
