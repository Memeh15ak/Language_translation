# 📝 Hindi-English PDF Translator App

A Streamlit web application that lets users upload a **PDF file** and translate its content between **Hindi ↔ English** while preserving structure and layout. Tables, images, and flowcharts are first extracted as readable text using Gemini, chunked, translated, and finally **recombined into a translated PDF**.

---
## Working Example
![Example](https://github.com/Memeh15ak/Language_translation/blob/master/media/Example.gif)



## 🚀 Features

- 📤 Upload any PDF (with text, tables, flowcharts, or images)
- 🔁 Two-way translation: English → Hindi or Hindi → English
- 🤖 Uses **Gemini LLM** for PDF content understanding
- ✂️ Chunk-based translation for large documents
- 🧠 Intelligent logic to preserve abbreviations and capitalized words
- 📄 Final output is a single, well-formatted translated PDF (via `fpdf2`)

---

## 🛠 Tech Stack

- **Frontend:** Streamlit
- **LLM:** Gemini (via Google Generative AI API)
- **Translation:** HuggingFace MarianMT (`Helsinki-NLP/opus-mt-en-hi` & `hi-en`)
- **PDF Parsing:** PyMuPDF
- **PDF Output:** `fpdf2` with Unicode font support
- **Chunking:** NLTK sentence tokenizer

---

## 📂 Project Structure

Translator/
├── app.py                          # Main Streamlit app
├── .env                           # API keys
├── requirements.txt               # Python dependencies
├── data/
│   └── sample.pdf                 # Test file
├── chunks/                        # Auto-created folder for text chunks
├── output.txt                     # Extracted full content from PDF
├── translated_output.pdf          # Final translated PDF
└── src/
    ├── extract_content.py         # Gemini-based PDF text extraction
    ├── preprocess.py              # Chunking logic
    └── convert.py                 # Translate & directly generate PDF
🚀 Quick Start
Prerequisites

Python 3.11+ (recommended)
Google Generative AI API key
Git

1. Clone the Repository
bashgit clone https://github.com/yourusername/pdf-translator-app.git
cd pdf-translator-app
2. Create Virtual Environment
bashpython -m venv ragenv
ragenv\Scripts\activate  # Windows
# or
source ragenv/bin/activate  # macOS/Linux
3. Install Dependencies
bashpip install -r requirements.txt
4. Download Required Font
Download Noto Sans Devanagari font and place NotoSansDevanagari-Regular.ttf in the /fonts directory.
5. Set Up Environment Variables
Create a .env file in the root directory:
iniGOOGLE_API_KEY=your_google_generativeai_api_key
To get your Google API key:

Visit Google AI Studio
Create a new API key
Copy and paste it into your .env file

6. Run the Application
bashstreamlit run app.py
The app will open in your default browser at http://localhost:8501
🎯 How to Use

Upload PDF: Click "Browse files" and select your PDF document
Extract Text: The app automatically extracts text using Gemini AI
Process: Text is chunked and processed for optimal translation
Translate: Each chunk is translated to Hindi
Download: Get your translated PDF with proper Unicode formatting

📋 Dependencies
Key libraries used:

streamlit - Web interface
google-generativeai - Gemini AI for text extraction and translation
PyPDF2 - PDF processing
reportlab - PDF generation
python-dotenv - Environment variable management

🖼️ Sample Usage

Input: sample.pdf (provided in /data folder)
Output: translated_output.pdf (auto-generated after processing)





