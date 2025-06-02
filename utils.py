import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Dict


# Thiết bị sử dụng: GPU nếu có, không thì dùng CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model dịch Anh -> Việt
en_vi_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-vi")
en_vi_model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-vi").to(device)

# Load model dịch Việt -> Anh
vi_en_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-vi-en")
vi_en_model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-vi-en").to(device)

def clean_text(text: str) -> str:
    """Làm sạch kết quả tóm tắt"""
    text = text.replace("_", " ")
    text = text.replace("COD 19", "COVID-19").replace("COD19", "COVID-19")
    text = text.replace("covid 19", "COVID-19").replace("covid19", "COVID-19")
    return text.strip()

def translate(text: str, tokenizer, model, max_length=512) -> str:
    """Dịch văn bản"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length).to(device)
    outputs = model.generate(**inputs, max_length=128, num_beams=4, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def summarize_text(text: str, model, tokenizer, max_length=64, min_length=30) -> str:
    """Tóm tắt văn bản"""
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
    return clean_text(summary)

def get_summary_length_params(length_option: str):
    """Chuyển đổi lựa chọn độ dài thành tham số cho mô hình"""
    length_option = length_option.lower()
    if length_option == "sieu ngan":
        return {"max_length": 30, "min_length": 10}
    elif length_option == "ngan":
        return {"max_length": 50, "min_length": 20}
    elif length_option == "binh thuong":
        return {"max_length": 80, "min_length": 30}
    else:
        return {"max_length": 64, "min_length": 30}
