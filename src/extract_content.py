import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  

def read_pdf_text(path):
    import fitz  
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def ask_gemini_to_process(text):
    prompt = f"""This PDF contains structured text with headings, paragraphs, and visuals such as flowcharts, tables, and charts.\n\n"
        "Your task is to:\n"
        "1. Extract the **entire written content exactly as it appears**, preserving all **headings, subheadings, and structure**.\n"
        "2. Do NOT summarize, rephrase, or omit any part of the text.\n"
        "3. For TABLES, convert to simple, embedding-friendly format:\n"
        "   - Keep it minimal and natural\n"
        "   - Example: 'Version V1.0 approved by Vernon Alcantra on 01/09/2015 for Document Created'\n"
        "   - Just state the facts simply without extra formatting\n"
        "   - Each table row becomes one clean sentence\n"
        "4. For flowcharts and diagrams:\n"
        "   - Important - use the exactly same words from the flowchart basically try to draw the flowchart with text instead of arrows add gramtical words like then and if there is text betwee arrows that modify two choices use that like if the results are more prior then this types"
        "   - Write the entire steps of the entire flowchart process with eaxct words\n"
        "   - Use the exact words and terminology from the flowchart\n"
        "   - Follow the logical flow and describe decision points and outcomes\n"
        
        "5. For regular text content:\n"
        "   - Preserve exactly as written\n"
        "   - Keep original structure\n"
        "6. Keep output clean and simple - good for embeddings and chunking\n"
        "7. No special markers, no extra formatting - just natural readable text\n\n"
        f"Content:\n{text}"""
    

    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def save_to_txt(text, filename="output.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    pdf_path = "data/398b3383-67bd-43ee-8e90-6c3b331c13a2.pdf"
    print("Reading PDF content...")
    text = read_pdf_text(pdf_path)
    print("Processing with Gemini 2.0 Flash...")
    output = ask_gemini_to_process(text)
    save_to_txt(output)
    print("Saved output to output.txt")

if __name__ == "__main__":
    main()
