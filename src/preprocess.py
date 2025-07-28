import fitz  
import os
from typing import List
import re
import nltk
from pathlib import Path
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text) 
    text = re.sub(r"\\n", " ", text)  
    return text.strip()

def split_into_chunks(text: str, max_words=400) -> List[str]:
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        word_count = len(sentence.split())

        if word_count > max_words:
            words = sentence.split()
            for i in range(0, len(words), max_words):
                chunks.append(" ".join(words[i:i+max_words]))
            continue

        if current_length + word_count <= max_words:
            current_chunk.append(sentence)
            current_length += word_count
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_length = word_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def save_chunks(chunks: List[str], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    for idx, chunk in enumerate(chunks):
        with open(f"{output_dir}/chunk_{idx}.txt", "w", encoding="utf-8") as f:
            f.write(chunk)

def preprocess_document(file_path: str, chunk_dir: str):
    raw_text = extract_text_from_pdf(file_path)
    cleaned = clean_text(raw_text)
    chunks = split_into_chunks(cleaned, max_words=800)
    save_chunks(chunks, chunk_dir)
    print(f"{len(chunks)} chunks saved to '{chunk_dir}'")
