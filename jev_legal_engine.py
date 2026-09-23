import asyncio
import os
import json
import time
from typing import List, Dict, Any, Optional
import httpx

TYPESAFE_API_URL = "https://api.typesafe.ai/v1/systemone"
CONSTITUTION_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "constitution_fa.json")

class JevLegalEngine:
    def __init__(self, data_path: str = CONSTITUTION_DATA_PATH):
        with open(data_path, "r", encoding="utf-8") as f:
            self.articles: List[Dict[str, Any]] = json.load(f)
            
    async def evaluate_single_article(
        self, 
        client: httpx.AsyncClient, 
        semaphore: asyncio.Semaphore, 
        article: Dict[str, Any], 
        query: str,
        api_key: str
    ) -> Dict[str, Any]:
        async with semaphore:
            payload = {
                "model": "jev-latest",
                "state": {
                    "article_id": article["id"],
                    "chapter": article.get("chapter", ""),
                    "text": article["text"]
                },
                "questions": {
                    "is_relevant": {
                        "type": "noul",
                        "instructions": f"آیا این اصل از قانون اساسی پاسخگوی پرسش حقوقی زیر است یا ارتباط مستقیم با آن دارد؟ پرسش: '{query}'"
                    },
                    "relevance_level": {
                        "type": "score",
                        "instructions": f"میزان تعیین‌کنندگی این اصل قانون اساسی را برای موضوع '{query}' سنجش کنید.",
                        "criteria": [
                            "بی‌ارتباط یا موضوع کاملاً متفاوت",
                            "اشاره ضمنی یا زمینه عمومی",
                            "حکم مستقیم، صریح و تعیین‌کننده"
                        ]
                    },
                    "rule_type": {
                        "type": "choice",
                        "instructions": f"نوع حکم صادرشده در این اصل قانون اساسی برای موضوع '{query}' چیست؟",
                        "criteria": {
                            "right_grant": "اعطای حق یا آزادی مصرح به شهروندان",
                            "obligation": "ایجاد تکلیف یا مسئولیت اجباری برای دولت یا نهادها",
                            "prohibition": "منع قانونی، ممنوعیت مطلق یا جرم‌انگاری",
                            "procedural": "تعیین ساختار، مهلت زمانی، مرجع صالح یا نحوه اجرا",
                            "none": "هیچ‌کدام"
                        }
                    }
                }
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                res = await client.post(TYPESAFE_API_URL, json=payload, headers=headers, timeout=15.0)
                res.raise_for_status()
                data = res.json()
                answers = data.get("answers", {})
                
                return {
                    "article": article,
                    "noul": answers.get("is_relevant", {}).get("noul", 0.0),
                    "score": answers.get("relevance_level", {}).get("score", 0.0),
                    "score_confidence": answers.get("relevance_level", {}).get("confidence", 0.0),
                    "choice": answers.get("rule_type", {}).get("choice", "none"),
                    "choice_confidence": answers.get("rule_type", {}).get("confidence", 0.0),
                    "tokens": data.get("usage", {})
                }
            except Exception as e:
                return {
                    "article": article,
                    "error": str(e),
                    "noul": 0.0,
                    "score": 0.0
                }

    async def search(
        self, 
        query: str, 
        api_key: Optional[str] = None, 
        threshold: float = 0.55, 
        max_concurrency: int = 30
    ) -> Dict[str, Any]:
        # Use provided api_key or environment variable
        effective_key = api_key or os.getenv("TYPESAFE_API_KEY", "").strip()
        
        if not effective_key:
            raise ValueError("کلید API تعریف نشده است. لطفاً کلید API خود را در تنظیمات وب‌سایت یا متغیر محیطی TYPESAFE_API_KEY وارد نمایید.")
            
        start_time = time.time()
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async with httpx.AsyncClient() as client:
            tasks = [
                self.evaluate_single_article(client, semaphore, art, query, effective_key)
                for art in self.articles
            ]
            results = await asyncio.gather(*tasks)
            
        elapsed = time.time() - start_time
        
        # Filter relevant matches
        matches = [r for r in results if r.get("noul", 0.0) >= threshold]
        matches.sort(key=lambda x: (x.get("noul", 0.0), x.get("score", 0.0)), reverse=True)
        
        total_input_tokens = sum(r.get("tokens", {}).get("input_tokens", 0) for r in results)
        total_output_tokens = sum(r.get("tokens", {}).get("output_tokens", 0) for r in results)
        
        approx_cost_usd = (total_input_tokens * 0.0000001) + (total_output_tokens * 0.0000003)
        
        return {
            "query": query,
            "total_articles_scanned": len(self.articles),
            "matched_articles_count": len(matches),
            "elapsed_seconds": round(elapsed, 2),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "approx_cost_usd": f"${approx_cost_usd:.5f}",
            "matches": matches
        }

if __name__ == "__main__":
    engine = JevLegalEngine()
    print(f"Loaded {len(engine.articles)} articles from constitution.")
