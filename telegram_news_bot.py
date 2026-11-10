"""
19-Maktab — Telegram Yangiliklar Boti
=====================================
Telegram orqali yuborilgan postlarni (matn + rasmlar)
avtomatik tarzda maktab saytiga yangilik qilib joylaydi!
"""

import os
import sys
import time
import uuid
import threading
import requests
from io import BytesIO

# Django muhitini yuklaymiz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone
from apps.news.models import News, NewsCategory, NewsImage

BOT_TOKEN = "8864775756:AAECLlA465NwQR0E-93CYy07HPiuSs2B7Ko"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Jonli sayt manzili
LIVE_SITE_URL = "https://one9maktab-nmg.onrender.com"
HEALTH_ENDPOINT = f"{LIVE_SITE_URL}/health/"


def send_telegram_message(chat_id, text, reply_markup=None):
    """Foydalanuvchiga Telegram xabari yuborish."""
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[TG XATOSI] Xabar yuborishda xato: {e}")


def get_file_bytes(file_id):
    """Telegram serveridan rasm faylini yuklab olish."""
    try:
        f_info = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}", timeout=10).json()
        if f_info.get("ok"):
            file_path = f_info["result"]["file_path"]
            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            resp = requests.get(download_url, timeout=25)
            if resp.status_code == 200:
                ext = file_path.split('.')[-1] if '.' in file_path else 'jpg'
                return resp.content, f"{uuid.uuid4().hex[:8]}.{ext}"
    except Exception as e:
        print(f"[YUKLASH XATOSI] Rasm yuklanmadi: {e}")
    return None, None


def parse_post_text(text):
    """Matnni chiroyli sarlavha va asosiy mazmunga ajratish."""
    if not text:
        return "19-maktab hayotidan yangilik", ""

    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    if not lines:
        return "19-maktab hayotidan yangilik", text

    first_line = lines[0]
    if len(first_line) > 130:
        sentences = first_line.split('.')
        title = sentences[0] if len(sentences[0]) < 130 else first_line[:125] + "..."
    else:
        title = first_line

    content = text.strip()
    return title, content


def save_news_to_django(title, content, cover_bytes, cover_filename):
    """Yangilikni to'g'ridan-to'g'ri Django bazasiga saqlash."""
    base_slug = slugify(title)
    if not base_slug:
        base_slug = f"news-{uuid.uuid4().hex[:8]}"
    
    slug = base_slug
    counter = 1
    while News.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    category, _ = NewsCategory.objects.get_or_create(
        name="Maktab yangiliklari",
        defaults={'slug': 'maktab-yangiliklari', 'color': '#4F46E5'}
    )

    excerpt = content[:200] + ('...' if len(content) > 200 else '')

    news_item = News(
        title=title,
        slug=slug,
        category=category,
        excerpt=excerpt,
        content=content,
        status='published',
        published_at=timezone.now(),
        is_featured=True
    )

    if cover_bytes:
        news_item.cover_image.save(cover_filename, ContentFile(cover_bytes), save=False)

    news_item.save()

    # Jonli saytga ham API orqali uzatishga urinib ko'ramiz
    try:
        api_url = f"{LIVE_SITE_URL}/news/api/create-from-bot/"
        files = {"cover_image": (cover_filename, BytesIO(cover_bytes), "image/jpeg")} if cover_bytes else {}
        requests.post(
            api_url,
            data={"title": title, "content": content, "excerpt": excerpt},
            files=files,
            headers={"X-Bot-Token": BOT_TOKEN},
            timeout=10
        )
    except Exception:
        pass

    return news_item


def handle_update(update):
    """Telegram yangilanishini qayta ishlash."""
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text") or message.get("caption") or ""
    photos = message.get("photo")

    # /start buyrug'i
    if text.strip().startswith("/start"):
        start_msg = (
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "Bu <b>19-sonli maktabning rasmiy sayt boti</b>.\n\n"
            "📰 <b>Saytga yangilik qo'shish juda oson:</b>\n"
            "Menga shunchaki <b>rasm</b> va uning tagiga <b>matnini</b> yuboring (yoki kanaldan postni forward qiling).\n\n"
            "Men uni darhol maktab veb-saytiga joylayman! 🚀"
        )
        markup = {
            "inline_keyboard": [
                [{"text": "🌐 Saytni ochish", "url": LIVE_SITE_URL}],
                [{"text": "⚙️ Admin panel", "url": f"{LIVE_SITE_URL}/dashboard/login/"}]
            ]
        }
        send_telegram_message(chat_id, start_msg, markup)
        return

    # /status buyrug'i
    if text.strip().startswith("/status"):
        try:
            t0 = time.time()
            r = requests.get(HEALTH_ENDPOINT, timeout=10)
            elapsed = round((time.time() - t0) * 1000)
            status_text = f"🟢 <b>Sayt faol va uyg'oq!</b>\n⏱ Javob vaqti: <b>{elapsed} ms</b>\n🔗 {LIVE_SITE_URL}"
        except Exception as e:
            status_text = f"🟡 <b>Sayt tekshirilmoqda...</b>\n{e}"
        send_telegram_message(chat_id, status_text)
        return

    # Yangilik qo'shish
    send_telegram_message(chat_id, "⏳ <i>Yangilik qabul qilindi, saytga joylanmoqda...</i>")

    cover_bytes = None
    cover_filename = "cover.jpg"

    if photos:
        best_photo = photos[-1]
        file_id = best_photo["file_id"]
        cover_bytes, cover_filename = get_file_bytes(file_id)

    title, content = parse_post_text(text)

    if not text and cover_bytes:
        title = f"19-maktab hayotidan fotolavha ({time.strftime('%d.%m.%Y')})"
        content = "Namangan tumani 19-sonli umumiy o'rta ta'lim maktabida o'tkazilgan tadbirlar va dars jarayonidan fotolavha."

    try:
        news_item = save_news_to_django(title, content, cover_bytes, cover_filename)
        news_url = f"{LIVE_SITE_URL}{news_item.get_absolute_url()}"

        reply_msg = (
            "✅ <b>Yangilik saytga muvaffaqiyatli joylandi!</b>\n\n"
            f"📌 <b>Sarlavha:</b> {news_item.title}\n"
            f"📅 <b>Sana:</b> {news_item.published_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"🔗 <b>Saytda ko'rish:</b>\n{news_url}"
        )
        markup = {
            "inline_keyboard": [
                [{"text": "👀 Yangilikni ko'rish", "url": news_url}],
                [{"text": "🌐 Asosiy sayt", "url": LIVE_SITE_URL}]
            ]
        }
        send_telegram_message(chat_id, reply_msg, markup)
        print(f"[OK] Yangilik muvaffaqiyatli saqlandi: {news_item.title} (slug: {news_item.slug})")
    except Exception as e:
        print(f"[XATO] Saqlashda xatolik: {e}")
        send_telegram_message(chat_id, f"❌ <b>Xatolik yuz berdi:</b> {e}\n\nIltimos, qaytadan urinib ko'ring.")


def keep_alive_daemon():
    """Fonda saytni har 5 daqiqada uyg'otib turuvchi robot."""
    while True:
        try:
            requests.get(HEALTH_ENDPOINT, timeout=15)
        except Exception:
            pass
        time.sleep(300)


def run_bot():
    """Telegram Botni doimiy eshitish (Polling) rejimida ishga tushirish."""
    print("=" * 60)
    print(" 19-Maktab Telegram Yangiliklar Boti ishga tushdi!")
    print(f" Bot manzili: @Xoldarxojayev_agent_ai_bot")
    print(" Post tashlang — darhol saytga joylanadi.")
    print("=" * 60)

    t = threading.Thread(target=keep_alive_daemon, daemon=True)
    t.start()

    offset = 0
    while True:
        try:
            resp = requests.get(f"{TELEGRAM_API}/getUpdates?offset={offset}&timeout=30", timeout=40)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        try:
                            handle_update(update)
                        except Exception as e:
                            print(f"[UPDATE XATOSI] {e}")
            elif resp.status_code == 409:
                time.sleep(4)
        except requests.exceptions.RequestException:
            time.sleep(3)
        except Exception as e:
            print(f"[KUTILMAGAN XATO] {e}")
            time.sleep(3)


if __name__ == "__main__":
    run_bot()
