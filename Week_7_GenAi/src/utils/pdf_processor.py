import pdfplumber
import pandas as pd

def extract_text_and_tables(pdf_path):
    processed_pages = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_content = ""

            tables = page.extract_tables()
            if tables:
                for table in tables:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    markdown_table = df.to_markdown(index=False)
                    page_content += f"\n\n{markdown_table}\n\n"

            text = page.extract_text()
            if text:
                page_content += text

            if page_content.strip():
                processed_pages.append({
                    "page": page_num,
                    "text": page_content
                })
                
    return processed_pages