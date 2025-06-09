from flask import Flask, request, jsonify, Response, render_template
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from models import SummaryHistory, SessionLocal

from utils import (
    device,
    translate,
    en_vi_tokenizer,
    en_vi_model,
    vi_en_tokenizer,
    vi_en_model,
    summarize_text,
    summarize_long_text,
)
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  

def custom_jsonify(data):
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        mimetype='application/json; charset=utf-8'
    )


summarize_model_path = "vit5_large_vn"
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

        if not text:
            return custom_jsonify({"error": "No input text provided."}), 400

        default_summary_params = {"max_length": 64, "min_length": 30}

        if source_lang == "en" and target_lang == "vi":
            translated_vi = translate(text, en_vi_tokenizer, en_vi_model)
            summary = summarize_long_text(
                translated_vi,
                summarize_model,
                summarize_tokenizer,
                **default_summary_params
            )
        elif source_lang == "vi" and target_lang == "en":
            summary_vi = summarize_long_text(
                text,
                summarize_model,
                summarize_tokenizer,
                **default_summary_params
            )
            summary = translate(summary_vi, vi_en_tokenizer, vi_en_model)
        else:
            summary = summarize_long_text(
                text,
                summarize_model,
                summarize_tokenizer,
                **default_summary_params
            )

        # Lưu vào DB
        db = SessionLocal()
        history = SummaryHistory(
            input_text=text,
            summary_text=summary,
            source_lang=source_lang,
            target_lang=target_lang
        )
        db.add(history)
        db.commit()
        db.close()

        return custom_jsonify({"summary": summary})

    except Exception as e:
        return custom_jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
def get_history():
    try:
        db = SessionLocal()
        histories = db.query(SummaryHistory).order_by(SummaryHistory.id.desc()).limit(20).all()
        db.close()

        result = [
            {
                "id": h.id,
                "source_lang": h.source_lang,
                "target_lang": h.target_lang,
                "input_text": h.input_text,
                "summary_text": h.summary_text,
                "timestamp": h.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for h in histories
        ]
        return custom_jsonify(result)

    except Exception as e:
        return custom_jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
