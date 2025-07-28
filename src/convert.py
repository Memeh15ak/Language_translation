import os
import re
from transformers import MarianMTModel, MarianTokenizer
import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt")

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

def translate_chunks_to_text(input_folder="chunks", output_file="translated_output.pdf", direction="en_to_hi"):
    """
    Save as text file instead of PDF to avoid encoding issues
    """
    tokenizer, model = load_translation_model(direction)
    
    with open(output_file, "w", encoding="utf-8") as output:
        for filename in sorted(os.listdir(input_folder)):
            if filename.endswith(".txt"):
                with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                    text = f.read()
                    translated = intelligent_translate(text, tokenizer, model)
                    
                    output.write(f"\n{'='*50}\n")
                    output.write(f"File: {filename}\n")
                    output.write(f"{'='*50}\n\n")
                    output.write(translated)
                    output.write("\n\n")
    
    print(f"Translated text file created : {output_file}")

if __name__ == "__main__":
    translate_chunks_to_text()