import asyncio
import os
from flask import Flask, render_template, request, jsonify
from jev_legal_engine import JevLegalEngine

app = Flask(__name__)
engine = JevLegalEngine()

@app.route("/")
def index():
    return render_template("index.html", total_articles=len(engine.articles))

@app.route("/api/search", methods=["POST"])
def search_api():
    data = request.json or {}
    query = data.get("query", "").strip()
    threshold = float(data.get("threshold", 0.55))
    api_key = data.get("api_key", "").strip() or os.getenv("TYPESAFE_API_KEY", "").strip()
    
    if not query:
        return jsonify({"error": "لطفاً پرسش حقوقی خود را وارد کنید."}), 400
        
    if not api_key:
        return jsonify({"error": "کلید API تعریف نشده است. لطفاً کلید API خود را در بالای صفحه (تنظیمات کلید API) وارد نموده یا متغیر محیطی TYPESAFE_API_KEY را مقداردهی نمایید."}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(engine.search(query, api_key=api_key, threshold=threshold))
    except Exception as e:
        return jsonify({"error": f"خطا در ارتباط یا ارزیابی: {str(e)}"}), 500
    finally:
        loop.close()
        
    return jsonify(results)

@app.route("/api/article/<article_id>", methods=["GET"])
def get_article(article_id):
    for art in engine.articles:
        if art["id"] == article_id:
            return jsonify(art)
    return jsonify({"error": "اصل مورد نظر یافت نشد."}), 404

if __name__ == "__main__":
    print("🚀 سامانه هوشمند تحلیل حقوقی قانون اساسی ایران در حال اجراست...")
    print("🌐 آدرس دسترسی: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
