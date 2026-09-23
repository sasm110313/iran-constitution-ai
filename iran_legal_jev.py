import asyncio
import os
import json
import time
from typing import List, Dict, Any
import httpx

# API Key provided by user
TYPESAFE_API_KEY = os.getenv(
    "TYPESAFE_API_KEY", 
    "apikey_20341ef74446864ceaa363b376da413038_d070ce2dc3cbca67c6eb2230d791754d859e6122e1d34f7ea465356eda6eb8c4"
)
TYPESAFE_API_URL = "https://api.typesafe.ai/v1/systemone"

# -----------------------------------------------------------------------------
# 1. پایگاه داده نمونه مواد قانونی (اصول قانون اساسی ایران + قوانین مدنی و مستأجر)
# -----------------------------------------------------------------------------
IRAN_CONSTITUTION_ARTICLES = [
    {
        "id": "اصل ۳",
        "title": "وظایف دولت جمهوری اسلامی",
        "text": "دولت جمهوری اسلامی ایران موظف است برای نیل به اهداف مذکور در اصل دوم، همه امکانات خود را برای امور زیر به کار برد: ایجاد محیط مساعد برای رشد فضایل اخلاقی، بالا بردن سطح آگاهی‌های عمومی، آموزش و پرورش رایگان، پیریزی اقتصاد صحیح و عادلانه، تامین حقوق همه جانبه افراد و ایجاد امنیت قضایی عادلانه."
    },
    {
        "id": "اصل ۱۹",
        "title": "برابری مردم ایران",
        "text": "مردم ایران از هر قوم و قبیله که باشند از حقوق مساوی برخوردارند و رنگ، نژاد، زبان و مانند اینها سبب امتیاز نخواهد بود."
    },
    {
        "id": "اصل ۲۰",
        "title": "حمايت قانونی برابر برای زن و مرد",
        "text": "همه افراد ملت اعم از زن و مرد یکسان در حمايت قانون قرار دارند و از همه حقوق انسانی، سیاسی، اقتصادی، اجتماعی و فرهنگی با رعایت موازین اسلام برخوردارند."
    },
    {
        "id": "اصل ۲۲",
        "title": "مصونیت حیثیت، جان، مال و مسکن",
        "text": "حیثیت، جان، مال، حقوق، مسکن و شغل اشخاص از تعرض مصون است مگر در مواردی که قانون تجویز کند."
    },
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
    },
    {
        "id": "اصل ۳۸",
        "title": "منع شکنجه و اجبار به اقرار",
        "text": "هر گونه شکنجه برای گرفتن اقرار و یا کسب اطلاع ممنوع است. اجبار شخص به شهادت، اقرار یا سوگند مجاز نیست و چنین شهادت و اقرار و سوگندی فاقد ارزش و اعتبار است. متخلف از این اصل طبق قانون مجازات می‌شود."
    },
    {
        "id": "اصل ۴۴",
        "title": "بخش‌های نظام اقتصادی ایران",
        "text": "نظام اقتصادی جمهوری اسلامی ایران بر پایه سه بخش دولتی، تعاونی و خصوصی با برنامه‌ریزی منظم و صحیح استوار است."
    },
    {
        "id": "اصل ۸۶",
        "title": "مصونیت پارلمانی نمایندگان مجلس",
        "text": "نمایندگان مجلس در مقام ایفای وظایف نمایندگی در اظهار نظر و رای خود کاملاً آزادند و نمی‌توان آنها را به سبب نظراتی که در مجلس اظهار کرده‌اند یا آرايی که در مقام ایفای وظایف نمایندگی خود داده‌اند تعقیب یا توقیف کرد."
    },
    {
        "id": "اصل ۱۱۳",
        "title": "جایگاه ریاست جمهوری",
        "text": "پس از مقام رهبری، رئیس‌جمهور عالی‌ترین مقام رسمی کشور است و مسئولیت اجرای قانون اساسی و ریاست قوه مجریه را جز در مواردی که مستقیماً به رهبری مربوط می‌شود، بر عهده دارد."
    },
    {
        "id": "ماده ۴ قانون روابط موجر و مستاجر ۱۳۷۶",
        "title": "تخلیه عين مستاجره و استرداد ودیعه",
        "text": "در صورتی که‌ موجر مبلغی به عنوان ودیعه یا تضمین یا قرض‌الحسنه و یا سند تعهدآور و مشابه آن از مستاجر دریافت کرده باشد، تخلیه و تحویل مورد اجاره به موجر موکول به استرداد سند یا وجه مذکور به مستاجر و یا سپردن آن به دائره اجراست."
    },
    {
        "id": "ماده ۵۲۲ قانون آئین دادرسی مدنی",
        "title": "خسارت تاخیر تادیه دین و ودیعه",
        "text": "در دعاویی که موضوع آن دین از نوع وجه رایج بوده و با مطالبه داین و تمکن مدیون، مدیون از پرداخت امتناع نماید، در صورت تغییر فاحش شاخص قیمت سالانه از زمان سررسید تا زمان پرداخت بر اساس شاخص سالانه بانک مرکزی، تغییر شاخص محاسباتی و پرداخت خواهد شد."
    }
]


# -----------------------------------------------------------------------------
# 2. موتور ارزیابی موازی با مدل Jev (System One)
# -----------------------------------------------------------------------------
async def evaluate_article_with_jev(client: httpx.AsyncClient, article: Dict[str, Any], user_query: str) -> Dict[str, Any]:
    """
    ارزیابی یک ماده/اصل قانونی در برابر پرسش حقوقی کاربر با استفاده از پریمیتیوهای Jev:
    1. Noul: آیا این ماده با پرسش مرتبط است؟ (پاسخ 0 تا 1)
    2. Score: میزان ارتباط و قطعیت حکم قانونی (0: بی‌ارتباط، 1: اشاره عمومی، 2: حکم مستقیم)
    3. Choice: نوع حکم (حق، تکلیف، منع، آیین اجرا)
    """
    payload = {
        "model": "jev-latest",
        "state": {
            "article_id": article["id"],
            "title": article["title"],
            "text": article["text"]
        },
        "questions": {
            "is_relevant": {
                "type": "noul",
                "instructions": f"آیا متن این ماده/اصل قانون پاسخگوی پرسش حقوقی زیر است یا ارتباط مستقیم با آن دارد؟ پرسش: '{user_query}'"
            },
            "relevance_level": {
                "type": "score",
                "instructions": f"میزان ارتباط و تعیین‌کنندگی این ماده قانون را برای پرسش '{user_query}' مشخص کنید.",
                "criteria": [
                    "کاملاً بی‌ارتباط یا موضوع متفاوت",
                    "اشاره عمومی و غیرمستقیم به موضوع",
                    "حکم قانونی مستقیم، صریح و تعیین‌کننده"
                ]
            },
            "rule_type": {
                "type": "choice",
                "instructions": f"نوع حکم قانونی صادر شده در این اصل/ماده قانون نسبت به موضوع '{user_query}' چیست؟",
                "criteria": {
                    "right_grant": "اعطای حق یا آزادی به شهروند/اشخاص",
                    "obligation": "ایجاد تکلیف یا مسئولیت اجباری برای دولت یا اشخاص",
                    "prohibition": "منع قانونی، جرم‌انگاری یا ممنوعیت مطلق",
                    "procedural": "تعیین آیین کار، مهلت زمانی، مرجع صالح یا نحوه اجرا",
                    "none": "هیچ‌کدام / بی‌ارتباط"
                }
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {TYPESAFE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = await client.post(TYPESAFE_API_URL, json=payload, headers=headers, timeout=12.0)
        response.raise_for_status()
        data = response.json()
        
        answers = data.get("answers", {})
        noul_score = answers.get("is_relevant", {}).get("noul", 0.0)
        relevance_score = answers.get("relevance_level", {}).get("score", 0.0)
        score_conf = answers.get("relevance_level", {}).get("confidence", 0.0)
        rule_choice = answers.get("rule_type", {}).get("choice", "none")
        choice_conf = answers.get("rule_type", {}).get("confidence", 0.0)
        
        return {
            "article": article,
            "is_relevant_noul": noul_score,
            "relevance_score": relevance_score,
            "score_confidence": score_conf,
            "rule_type": rule_choice,
            "choice_confidence": choice_conf,
            "tokens": data.get("usage", {})
        }
    except Exception as e:
        return {
            "article": article,
            "error": str(e),
            "is_relevant_noul": 0.0,
            "relevance_score": 0.0
        }


# -----------------------------------------------------------------------------
# 3. خط لوله جستجو و تحلیل موازی حقوقی (Fan-Out Pipeline)
# -----------------------------------------------------------------------------
async def search_legal_corpus(user_query: str, min_noul_threshold: float = 0.60):
    print(f"\n🔍 در حال بررسی حقوقی با مدل Jev برای پرسش:")
    print(f"   «{user_query}»\n")
    print(f"📊 تعداد کل مواد/اصول قانونی در پایگاه داده: {len(IRAN_CONSTITUTION_ARTICLES)} اصل/ماده")
    print("🚀 ارسال درخواست‌های ارزیابی موازی (Parallel System One Evaluations)...\n")

    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        tasks = [
            evaluate_article_with_jev(client, article, user_query)
            for article in IRAN_CONSTITUTION_ARTICLES
        ]
        results = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time

    # فیلتر و مرتب‌سازی بر اساس احتمالات کالیبره‌شده Jev (noul > threshold)
    relevant_matches = [
        res for res in results 
        if res.get("is_relevant_noul", 0.0) >= min_noul_threshold
    ]
    
    # مرتب‌سازی بر اساس ترکیبی از احتمال Noul و امتیاز Score
    relevant_matches.sort(
        key=lambda x: (x.get("is_relevant_noul", 0.0), x.get("relevance_score", 0.0)),
        reverse=True
    )

    total_input_tokens = sum(r.get("tokens", {}).get("input_tokens", 0) for r in results)
    total_output_tokens = sum(r.get("tokens", {}).get("output_tokens", 0) for r in results)

    print(f"⚡ زمان کل ارزیابی {len(IRAN_CONSTITUTION_ARTICLES)} بخش قانونی: {elapsed:.2f} ثانیه")
    print(f"📈 توکن‌های مصرفی: {total_input_tokens} ورود / {total_output_tokens} خروج (هزینه تقریبی: زیر ۱ سنت)")
    print(f"🎯 تعداد قوانین مرتبط کشف شده: {len(relevant_matches)} اصل/ماده قانون\n")
    print("=" * 80)
    print("📌 نتایج حقوقی استخراج‌شده بر اساس مدل Jev:")
    print("=" * 80)

    if not relevant_matches:
        print("❌ هیچ اصل یا ماده قانونی مستقیمی با این میزان قطعیت پیدا نشد.")
        return

    for idx, match in enumerate(relevant_matches, 1):
        art = match["article"]
        noul_val = match["is_relevant_noul"]
        rel_score = match["relevance_score"]
        rule_type = match["rule_type"]
        conf = match["choice_confidence"]
        
        print(f"\n[{idx}] {art['id']} - {art['title']}")
        print(f"    📜 متن: {art['text']}")
        print(f"    🎯 احتمال ارتباط (Noul Probability): {noul_val * 100:.1f}%")
        print(f"    ⭐ امتیاز تعیین‌کنندگی (Score 0-2): {rel_score:.2f}")
        print(f"    ⚖️  دسته‌بندی حکم (Choice): {rule_type} (اطمینان: {conf * 100:.0f}%)")
        print("-" * 80)


# -----------------------------------------------------------------------------
# 4. اجرا و تست سناریوها
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # سناریو ۱: پرسش درباره حق دادخواهی و بازداشت
    user_query_1 = "اگر کسی را بازداشت کنند چقدر وقت دارند پرونده را به دادگاه بفرستند؟"
    asyncio.run(search_legal_corpus(user_query_1))

    print("\n" + "#" * 80 + "\n")

    # سناریو ۲: استرداد ودیعه مستأجر
    user_query_2 = "شرایط بازگرداندن پول ودیعه مستأجر توسط صاحبخونه موقع تخلیه چگونه است؟"
    asyncio.run(search_legal_corpus(user_query_2))
