import asyncio
import os
import json
import time
from typing import List, Dict, Any
import httpx

# API Key read from environment variable TYPESAFE_API_KEY
TYPESAFE_API_KEY = os.getenv("TYPESAFE_API_KEY", "")
TYPESAFE_API_URL = "https://api.typesafe.ai/v1/systemone"

# -----------------------------------------------------------------------------
# ۱. پایگاه داده مواد/اصول قانونی
# -----------------------------------------------------------------------------
IRAN_CONSTITUTION_ARTICLES = [
    {
        "id": "اصل ۳۲",
        "title": "منع دستگیری و بازداشت غیرقانونی",
        "text": "هیچ‌کس را نمی‌توان دستگیر کرد مگر به حکم و ترتیبی که قانون معین می‌کند. در صورت بازداشت، موضوع اتهام باید با ذکر دلایل بلافاصله کتباً به متهم ابلاغ و تفهیم شود و حداکثر ظرف ۲۴ ساعت پرونده مقدماتی به مراجع صالحه قضایی ارسال و مقدمات محاکمه، در اسرع وقت فراهم گردد."
    },
    {
        "id": "اصل ۳۴",
        "title": "حق دادخواهی و مراجعه به دادگاه",
        "text": "دادخواهی حق مسلم هر فرد است و هر کس می‌تواند به منظور دادخواهی به دادگاه‌های صالح مراجعه نماید. همه افراد ملت حق دارند این‌گونه دادگاه‌ها را در دسترس داشته باشند و هیچ‌کس را نمی‌توان از دادگاهی که به موجب قانون حق مراجعه به آن را دارد منع کرد."
    },
    {
        "id": "اصل ۳۵",
        "title": "حق انتخاب وکیل در دادگاه",
        "text": "در همه دادگاه‌ها طرفین دعوی حق دارند برای خود وکیل انتخاب نمایند و اگر توانایی انتخاب وکیل را نداشته باشند باید برای آنها امکانات تعیین وکیل فراهم گردد."
    },
    {
        "id": "اصل ۳۷",
        "title": "اصل برائت",
        "text": "اصل، برائت است و هیچ‌کس از نظر قانون مجرم شناخته نمی‌شود، مگر این که جرم او در دادگاه صالح ثابت گردد."
    }
]

async def evaluate_article(client: httpx.AsyncClient, article: Dict[str, Any], user_query: str) -> Dict[str, Any]:
    if not TYPESAFE_API_KEY:
        raise ValueError("لطفاً متغیر محیطی TYPESAFE_API_KEY را مقداردهی نمایید.")

    payload = {
        "model": "jev-latest",
        "state": article,
        "questions": {
            "is_relevant": {
                "type": "noul",
                "instructions": f"آیا این اصل قانونی مرتبط با پرسش زیر است؟ '{user_query}'"
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {TYPESAFE_API_KEY}",
        "Content-Type": "application/json"
    }

    res = await client.post(TYPESAFE_API_URL, json=payload, headers=headers)
    res.raise_for_status()
    return res.json()

if __name__ == "__main__":
    if not TYPESAFE_API_KEY:
        print("❌ متغیر محیطی TYPESAFE_API_KEY یافت نشد. لطفاً آن را مقداردهی کنید:")
        print("export TYPESAFE_API_KEY='your_api_key_here'")
    else:
        print("✅ کلید API شناسایی شد.")
