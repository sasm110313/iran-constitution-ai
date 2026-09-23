import asyncio
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
    
    if not query:
        return jsonify({"error": "لطفاً پرسش حقوقی خود را وارد کنید."}), 400
        
    # Run async search using asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(engine.search(query, threshold=threshold))
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
    print("🚀 سامانه هوشمند تحلیل حقوقی قانون اساسی ایران با مدل Jev در حال اجراست...")
    print("🌐 آدرس دسترسی: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
