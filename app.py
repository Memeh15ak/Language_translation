import streamlit as st
import os
import sys
import shutil
import re
from transformers import MarianMTModel, MarianTokenizer
import nltk
from nltk.tokenize import sent_tokenize

# Paths
SRC_DIR = os.path.join(os.getcwd(), "src")
CHUNKS_DIR = "chunks"
TRANSLATED_OUTPUT = "translated_output.txt"  # Changed to .txt
DOC_PATH = "output.txt"

# Add src to Python path
sys.path.append(SRC_DIR)

# Download NLTK data
nltk.download("punkt")

# Imports from your own modules
from src.extract_content import read_pdf_text, ask_gemini_to_process, save_to_txt
from src.preprocess import preprocess_document

# Translation functions (from your new converter)
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

# UI
st.title("📄 Hindi ↔ English PDF Translator")
st.markdown("---")

# File uploader
uploaded_pdf = st.file_uploader(
    "Upload PDF File", 
    type="pdf",
    help="Upload a PDF file to translate"
)

# Translation direction selector
direction = st.selectbox(
    "Select Translation Direction", 
    ["English to Hindi", "Hindi to English"],
    help="Choose the direction for translation"
)

# Main processing
if uploaded_pdf:
    # Save uploaded file
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_pdf.read())
    
    st.success("✅ PDF uploaded successfully.")
    
    # Display file info
    file_details = {
        "Filename": uploaded_pdf.name,
        "File size": f"{uploaded_pdf.size} bytes",
        "Translation direction": direction
    }
    
    with st.expander("📋 File Details"):
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")

    # Translation button
    if st.button("🚀 Translate PDF", type="primary"):
        try:
            # Step 1: Extract content
            with st.spinner("🔍 Extracting content using Gemini..."):
                text = read_pdf_text("temp.pdf")
                output = ask_gemini_to_process(text)
                save_to_txt(output)
                st.success("✅ Text extracted and saved")

            # Step 2: Chunk the document
            with st.spinner("📚 Chunking the text..."):
                preprocess_document(DOC_PATH, CHUNKS_DIR)
                st.success("✅ Document chunked successfully")

            # Step 3: Translate chunks
            with st.spinner("🌐 Translating chunks... (This may take a while)"):
                translated_file = translate_chunks_to_text(
                    input_folder=CHUNKS_DIR,
                    output_file=TRANSLATED_OUTPUT,
                    direction="en_to_hi" if direction == "English to Hindi" else "hi_to_en"
                )
                st.success("✅ Translation completed!")

            # Step 4: Display results and download
            st.markdown("---")
            st.subheader("📄 Translation Results")
            
            # Read and display preview
            with open(translated_file, "r", encoding="utf-8") as f:
                translated_content = f.read()
            
            # Show preview
            with st.expander("👀 Preview Translated Content"):
                preview_length = 1000
                if len(translated_content) > preview_length:
                    st.text_area(
                        "Content Preview",
                        translated_content[:preview_length] + "\n\n... (showing first 1000 characters)",
                        height=200
                    )
                else:
                    st.text_area("Full Content", translated_content, height=200)
            
            # Download button
            st.download_button(
                label="📥 Download Translated Document",
                data=translated_content,
                file_name=f"translated_{uploaded_pdf.name.replace('.pdf', '.txt')}",
                mime="text/plain",
                type="primary"
            )
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Characters", len(translated_content))
            with col2:
                st.metric("Words", len(translated_content.split()))
            with col3:
                chunk_count = len([f for f in os.listdir(CHUNKS_DIR) if f.endswith('.txt')]) if os.path.exists(CHUNKS_DIR) else 0
                st.metric("Chunks Processed", chunk_count)

        except Exception as e:
            st.error(f"❌ An error occurred during translation: {str(e)}")
            st.info("Please try uploading a different PDF or check if the file is corrupted.")
        
        finally:
            # Cleanup temporary files
            cleanup_files = ["temp.pdf", DOC_PATH, TRANSLATED_OUTPUT]
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

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ Information")
    st.markdown("""
    ### How it works:
    1. **Upload** your PDF file
    2. **Select** translation direction
    3. **Click** translate to process
    4. **Download** the translated text file
    
    ### Supported formats:
    - Input: PDF files
    - Output: Text files (.txt)
    
    ### Features:
    - Preserves document structure
    - Handles large documents
    - Maintains formatting
    - Unicode support
    """)
    
    st.markdown("---")
    st.markdown("**Note:** Translation may take several minutes for large documents.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with ❤️ using Streamlit | AI-Powered Translation"
    "</div>",
    unsafe_allow_html=True
)