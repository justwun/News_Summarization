import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Dict, List
import re

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

en_vi_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-vi")
en_vi_model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-vi").to(device)

vi_en_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-vi-en")
vi_en_model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-vi-en").to(device)

def clean_text(text: str) -> str:
    """Làm sạch kết quả tóm tắt"""
    text = text.replace("_", " ")
    text = text.replace("COD 19", "COVID-19").replace("COD19", "COVID-19")
    text = text.replace("covid 19", "COVID-19").replace("covid19", "COVID-19")
    return text.strip()

def translate(text: str, tokenizer, model, max_length=512) -> str:
    print("\n--- [MODEL] Translation started ---")
    print("Input preview:", text[:100], "...")
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length).to(device)
    outputs = model.generate(**inputs, max_length=128, num_beams=4, early_stopping=True)
    translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Translation result preview:", translated[:100], "...")
    print("--- [MODEL] Translation completed ---\n")
    return translated

def summarize_text(text: str, model, tokenizer, max_length=64, min_length=30) -> str:
    """Tóm tắt văn bản ngắn"""
    print("\n--- [MODEL] Summarization started ---")
    print("Input length:", len(text))
    print("Input preview:", text[:100], "...")
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
    summary_ids = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=max_length,
        min_length=min_length,
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=3
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    cleaned = clean_text(summary)
    print("Summary result preview:", cleaned[:100], "...")
    print("--- [MODEL] Summarization completed ---\n")
    return cleaned

def chunk_text(text: str, max_words: int = 400) -> List[str]:
    """Chia văn bản thành các đoạn nhỏ theo số từ"""
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def summarize_long_text(
    text: str,
    model,
    tokenizer,
    max_length: int = 64,
    min_length: int = 30,
    max_chunks: int = 2
) -> str:
    print("\n--- [MODEL] Long-text summarization started ---")
    print("Original word count:", len(text.split()))
    chunks = chunk_text(text, max_words=400)
    print("Number of chunks created:", len(chunks))

    too_long = len(chunks) > max_chunks
    if too_long:
        print("⚠️ Text too long – truncating to", max_chunks, "chunks.")
        chunks = chunks[:max_chunks]

    summaries = []
    for idx, chunk in enumerate(chunks):
        print(f"\n[Chunk {idx + 1}] Summarizing...")
        summary = summarize_text(chunk, model, tokenizer, max_length=max_length, min_length=min_length)
        summaries.append(summary)

    result = "\n".join(summaries)
    if too_long:
        result += "\n\n⚠️ Văn bản quá dài, chỉ tóm tắt một phần."

    print("--- [MODEL] Long-text summarization completed ---\n")
    return result
