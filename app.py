from flask import Flask, request, jsonify, Response, render_template
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from utils import (
    device,
    translate,
    en_vi_tokenizer,
    en_vi_model,
    vi_en_tokenizer,
    vi_en_model,
    summarize_text,
    get_summary_length_params,
)
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Đảm bảo trả UTF-8 JSON đúng

def custom_jsonify(data):
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        mimetype='application/json; charset=utf-8'
    )

# Load mô hình ViT5 đã fine-tuned (hoặc thay bằng ./vit5_finetuned_2 nếu bạn đã train)
summarize_model_path = "./vit5_finetuned_2"
summarize_tokenizer = AutoTokenizer.from_pretrained(summarize_model_path)
summarize_model = AutoModelForSeq2SeqLM.from_pretrained(summarize_model_path).to(device)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/summarize_translate", methods=["POST"])
def summarize_translate():
    try:
        data = request.get_json()
        text = data.get("text", "")
        source_lang = data.get("source_lang", "vi")
        target_lang = data.get("target_lang", "vi")
        length_option = data.get("summary_length", "binh thuong")

        if not text:
            return custom_jsonify({"error": "No input text provided."}), 400

        length_params = get_summary_length_params(length_option)

        if source_lang == "en" and target_lang == "vi":
            translated_vi = translate(text, en_vi_tokenizer, en_vi_model)
            summary = summarize_text(
                translated_vi,
                summarize_model,
                summarize_tokenizer,
                **length_params
            )
            return custom_jsonify({"summary": summary})

        elif source_lang == "vi" and target_lang == "en":
            summary_vi = summarize_text(
                text,
                summarize_model,
                summarize_tokenizer,
                **length_params
            )
            translated_en = translate(summary_vi, vi_en_tokenizer, vi_en_model)
            return custom_jsonify({"summary": translated_en})

        else:
            summary = summarize_text(
                text,
                summarize_model,
                summarize_tokenizer,
                **length_params
            )
            return custom_jsonify({"summary": summary})

    except Exception as e:
        return custom_jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
