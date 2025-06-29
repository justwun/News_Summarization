from flask import Flask, request, jsonify, Response, render_template, session
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from models import SummaryHistory, SessionLocal, User
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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
app.secret_key = "T!q9Xv#Lr2@z*GmN7Y^fWs0eJk$Up&Eb"


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "20 per hour"]
)

def custom_jsonify(data):
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        mimetype='application/json; charset=utf-8'
    )

def error_response(message: str, code: int = 500):
    return custom_jsonify({
        "status": "error",
        "code": code,
        "message": message
    }), code

summarize_model_path = "vit5_finetuned_2"
summarize_tokenizer = AutoTokenizer.from_pretrained(summarize_model_path)
summarize_model = AutoModelForSeq2SeqLM.from_pretrained(summarize_model_path).to(device)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "")
        if not username or not password:
            return error_response("Tên đăng nhập và mật khẩu là bắt buộc.", 400)

        db = SessionLocal()
        user = db.query(User).filter_by(username=username).first()
        db.close()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            return custom_jsonify({"message": "Đăng nhập thành công."})
        return error_response("Tên đăng nhập hoặc mật khẩu không đúng.", 401)
    except Exception:
        return error_response("Đã xảy ra lỗi trong quá trình đăng nhập.", 500)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return custom_jsonify({"message": "Đã đăng xuất."})

@app.route("/summarize_translate", methods=["POST"])
@limiter.limit("5 per minute")
def summarize_translate():
    try:
        data = request.get_json()
        text = data.get("text", "")
        source_lang = data.get("source_lang", "vi")
        target_lang = data.get("target_lang", "vi")
        max_chunks = int(data.get("max_chunks", 2))

        if not text:
            return error_response("Không có văn bản đầu vào được cung cấp.", 400)

        default_summary_params = {"max_length": 64, "min_length": 30}

        if source_lang == "en" and target_lang == "vi":
            translated_vi = translate(text, en_vi_tokenizer, en_vi_model)
            summary = summarize_long_text(
                translated_vi,
                summarize_model,
                summarize_tokenizer,
                **default_summary_params,
                max_chunks=max_chunks
            )
        elif source_lang == "vi" and target_lang == "en":
            summary_vi = summarize_long_text(
                text,
                summarize_model,
                summarize_tokenizer,
                **default_summary_params,
                max_chunks=max_chunks
            )
            summary = translate(summary_vi, vi_en_tokenizer, vi_en_model)
        else:
            summary = summarize_long_text(
                text,
                summarize_model,
                summarize_tokenizer,
                **default_summary_params,
                max_chunks=max_chunks
            )

        db = SessionLocal()
        user_id = session.get("user_id")
        if user_id:
            history = SummaryHistory(
                original_text=text,
                summary=summary,
                source_lang=source_lang,
                target_lang=target_lang,
                user_id=user_id
            )
            db.add(history)
            db.commit()
        db.close()

        return custom_jsonify({"summary": summary})

    except SQLAlchemyError:
        return error_response("Lỗi cơ sở dữ liệu xảy ra trong quá trình tóm tắt.", 500)
    except Exception:
        return error_response("Không thể tóm tắt văn bản. Vui lòng kiểm tra đầu vào của bạn.", 500)

@app.route("/history", methods=["GET"])
def get_history():
    user_id = session.get("user_id")
    if not user_id:
        return error_response("Cần đăng nhập để xem lịch sử.", 401)
    try:
        db = SessionLocal()
        histories = db.query(SummaryHistory).filter_by(user_id=user_id).order_by(SummaryHistory.id.desc()).limit(20).all()
        db.close()

        result = [
            {
                "id": h.id,
                "source_lang": h.source_lang,
                "target_lang": h.target_lang,
                "input_text": h.original_text,
                "summary_text": h.summary,
                "timestamp": h.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for h in histories
        ]
        return custom_jsonify(result)

    except SQLAlchemyError:
        return error_response("Lỗi cơ sở dữ liệu khi truy xuất lịch sử.", 500)
    except Exception:
        return error_response("Lỗi không mong muốn khi truy xuất lịch sử.", 500)

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return error_response("Tên đăng nhập và mật khẩu là bắt buộc.", 400)

        db = SessionLocal()
        user = User(username=username)
        user.set_password(password)
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            db.close()
            return error_response("Tên đăng nhập đã tồn tại.", 409)
        db.close()
        return custom_jsonify({"message": "Tạo tài khoản thành công."}), 201

    except Exception:
        return error_response("Đã xảy ra lỗi trong quá trình đăng ký.", 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
