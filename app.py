import streamlit as st
import os
import sys
import shutil
import re
from transformers import MarianMTModel, MarianTokenizer
import nltk
from nltk.tokenize import sent_tokenize
import subprocess
import base64

SRC_DIR = os.path.join(os.getcwd(), "src")
CHUNKS_DIR = "chunks"
TRANSLATED_OUTPUT = "translated_output.txt"
FINAL_PDF = "final.pdf"
DOC_PATH = "output.txt"

sys.path.append(SRC_DIR)

nltk.download("punkt", quiet=True)
from src.extract_content import read_pdf_text, ask_gemini_to_process, save_to_txt
from src.preprocess import preprocess_document

def load_translation_model(direction="en_to_hi"):
    model_name = "Helsinki-NLP/opus-mt-en-hi" if direction == "en_to_hi" else "Helsinki-NLP/opus-mt-hi-en"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model

def intelligent_translate(text, tokenizer, model):
    preserved = re.findall(r'\b[A-Z]{2,}\b', text)
    for word in preserved:
        text = text.replace(word, f"[{word}]")
    
    sentences = sent_tokenize(text)
    translated_sentences = []
    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True)
        outputs = model.generate(**inputs)
        translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        for word in preserved:
            translated = translated.replace(f"[{word}]", word)
        translated_sentences.append(translated)
    
    return "\n".join(translated_sentences)

def translate_chunks_to_text(input_folder="chunks", output_file="translated_output.txt", direction="en_to_hi"):
    """
    Translate chunks and save as text file
    """
    tokenizer, model = load_translation_model(direction)
    
    with open(output_file, "w", encoding="utf-8") as output:
        output.write("TRANSLATED DOCUMENT\n")
        output.write("="*60 + "\n\n")
        
        for filename in sorted(os.listdir(input_folder)):
            if filename.endswith(".txt"):
                with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                    text = f.read()
                    translated = intelligent_translate(text, tokenizer, model)
                    
                    output.write(f"Section: {filename}\n")
                    output.write("-" * 40 + "\n")
                    output.write(translated)
                    output.write("\n\n")
    
    print(f"✅ Translated text file created at: {output_file}")
    return output_file

def convert_txt_to_pdf():
    """
    Convert translated text to PDF using the txt_to_pdf.py script
    """
    try:
        txt_to_pdf_path = os.path.join(SRC_DIR, "txt_to_pdf.py")
        result = subprocess.run([sys.executable, txt_to_pdf_path], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("PDF conversion successful")
            return True
        else:
            print(f" PDF conversion failed: {result.stderr}")
            return False
    except Exception as e:
        print(f" Error running PDF conversion: {str(e)}")
        return False

def display_pdf(pdf_path):
    """
    Display PDF in Streamlit
    """
    try:
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")
        return False

def get_pdf_download_link(pdf_path, filename):
    """
    Generate download link for PDF
    """
    try:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        
        b64_pdf = base64.b64encode(pdf_data).decode()
        return pdf_data
    except Exception as e:
        st.error(f"Error creating download link: {str(e)}")
        return None

st.title("📄 Hindi ↔ English PDF Translator")
st.markdown("---")

uploaded_pdf = st.file_uploader(
    "Upload PDF File", 
    type="pdf",
    help="Upload a PDF file to translate"
)

direction = st.selectbox(
    "Select Translation Direction", 
    ["English to Hindi", "Hindi to English"],
    help="Choose the direction for translation"
)

if uploaded_pdf:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_pdf.read())
    
    st.success("✅ PDF uploaded successfully.")
   
    file_details = {
        "Filename": uploaded_pdf.name,
        "File size": f"{uploaded_pdf.size} bytes",
        "Translation direction": direction
    }
    
    with st.expander("📋 File Details"):
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")

    if st.button("🚀 Translate PDF", type="primary"):
        try:
            with st.spinner("🔍 Extracting content using Gemini..."):
                text = read_pdf_text("temp.pdf")
                output = ask_gemini_to_process(text)
                save_to_txt(output)
                st.success("✅ Text extracted and saved")

            with st.spinner("📚 Chunking the text..."):
                preprocess_document(DOC_PATH, CHUNKS_DIR)
                st.success("✅ Document chunked successfully")

            with st.spinner("🌐 Translating chunks... (This may take a while)"):
                translated_file = translate_chunks_to_text(
                    input_folder=CHUNKS_DIR,
                    output_file=TRANSLATED_OUTPUT,
                    direction="en_to_hi" if direction == "English to Hindi" else "hi_to_en"
                )
                st.success("✅ Translation completed!")

            # Step 4: Convert to PDF
            with st.spinner("📄 Converting to PDF..."):
                pdf_success = convert_txt_to_pdf()
                if pdf_success:
                    st.success("✅ PDF conversion completed!")
                else:
                    st.error(" PDF conversion failed!")
                    raise Exception("PDF conversion failed")

            st.markdown("---")
            st.subheader("📄 Translation Results")
      
            with open(translated_file, "r", encoding="utf-8") as f:
                translated_content = f.read()
           
            with st.expander("👀 Preview Translated Text"):
                preview_length = 1000
                if len(translated_content) > preview_length:
                    st.text_area(
                        "Content Preview",
                        translated_content[:preview_length] + "\n\n... (showing first 1000 characters)",
                        height=200
                    )
                else:
                    st.text_area("Full Content", translated_content, height=200)
    
            st.subheader("📖 Final PDF")
            if os.path.exists(FINAL_PDF):
                if not display_pdf(FINAL_PDF):
                    st.info("PDF preview not available in this browser. Please download to view.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 Download Text File",
                        data=translated_content,
                        file_name=f"translated_{uploaded_pdf.name.replace('.pdf', '.txt')}",
                        mime="text/plain"
                    )
                
                with col2:
                    pdf_data = get_pdf_download_link(FINAL_PDF, f"translated_{uploaded_pdf.name}")
                    if pdf_data:
                        st.download_button(
                            label="📥 Download PDF File",
                            data=pdf_data,
                            file_name=f"translated_{uploaded_pdf.name}",
                            mime="application/pdf",
                            type="primary"
                        )
            else:
                st.error("PDF file not found!")
            
            # Statistics
            st.markdown("---")
            st.subheader("📊 Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Characters", len(translated_content))
            with col2:
                st.metric("Words", len(translated_content.split()))
            with col3:
                chunk_count = len([f for f in os.listdir(CHUNKS_DIR) if f.endswith('.txt')]) if os.path.exists(CHUNKS_DIR) else 0
                st.metric("Chunks Processed", chunk_count)
            with col4:
                pdf_size = os.path.getsize(FINAL_PDF) if os.path.exists(FINAL_PDF) else 0
                st.metric("PDF Size", f"{pdf_size:,} bytes")

        except Exception as e:
            st.error(f"Error occurred during translation: {str(e)}")
            st.info("Try uploading a different PDF")
        
        finally:
            cleanup_files = ["temp.pdf", DOC_PATH]  
            cleanup_dirs = [CHUNKS_DIR]
            
            for file_path in cleanup_files:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
            
            for dir_path in cleanup_dirs:
                if os.path.exists(dir_path):
                    try:
                        shutil.rmtree(dir_path)
                    except:
                        pass

with st.sidebar:
    st.header("ℹ️ Information")
    st.markdown("""
    ### How it works:
    1. **Upload** your PDF file
    2. **Select** translation direction
    3. **Click** translate to process
    4. **View** the translated PDF
    5. **Download** both text and PDF files
    
    ### Supported formats:
    - Input: PDF files
    - Output: Text files (.txt) & PDF files (.pdf)
    
    ### Features:
    - Preserves document structure
    - Handles large documents
    - Creates formatted PDF output
    - Unicode support for Hindi
    - PDF viewer integration
    """)
    
    st.markdown("---")
    st.markdown("**Note:** Translation may take several minutes for large documents.")

with st.sidebar:
    st.markdown("---")
    if st.button("🧹 Clear All Files"):
        cleanup_files = [TRANSLATED_OUTPUT, FINAL_PDF]
        for file_path in cleanup_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    st.success(f"Removed {file_path}")
                except:
                    st.error(f"Failed to remove {file_path}")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with ❤️ using Streamlit | AI-Powered Translation with PDF Output"
    "</div>",
    unsafe_allow_html=True
)