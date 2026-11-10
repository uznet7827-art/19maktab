"""
19-Maktab — Telegram Yangiliklar Boti
=====================================
Ushbu bot Telegram orqali yuborilgan postlarni (matn + rasmlar)
avtomatik tarzda maktab rasmiy saytiga yangilik qilib joylaydi!

Foydalanish:
1. Botga /start buyrug'ini yuboring.
2. Botga matn yoki rasm (tagida matni bilan) yuboring.
3. Bot yangilikni saytga chiqaradi va tayyor havolani qaytaradi.
4. Fonda har 5 daqiqada saytni uyg'otib turadi (Render uxlamaydi).
"""

import os
import sys
import time
import threading
import requests
from io import BytesIO

BOT_TOKEN = "8864775756:AAECLlA465NwQR0E-93CYy07HPiuSs2B7Ko"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Sayt manzillari
LIVE_SITE_URL = "https://one9maktab-nmg.onrender.com"
CUSTOM_DOMAIN_URL = "https://nmg-19maktab.uz"
API_ENDPOINT = f"{LIVE_SITE_URL}/news/api/create-from-bot/"
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
                return resp.content, f"image.{ext}"
    except Exception as e:
        print(f"[YUKLASH XATOSI] Rasm yuklanmadi: {e}")
    return None, None


def publish_to_website(title, content, cover_bytes=None, cover_filename="cover.jpg"):
    """Maktab saytiga yangilikni e'lon qilish."""
    headers = {
        "X-Bot-Token": BOT_TOKEN
    }
    data = {
        "title": title,
        "content": content,
        "excerpt": content[:180] + ("..." if len(content) > 180 else ""),
        "category": "Maktab yangiliklari"
    }

    files = {}
    if cover_bytes:
        files["cover_image"] = (cover_filename, BytesIO(cover_bytes), "image/jpeg")

    try:
        resp = requests.post(API_ENDPOINT, data=data, files=files, headers=headers, timeout=40)
        return resp.json()
    except Exception as e:
        # Fallback to localhost if live site is updating
        try:
            resp = requests.post("http://127.0.0.1:8000/news/api/create-from-bot/", data=data, files=files, headers=headers, timeout=10)
            return resp.json()
        except Exception:
            return {"status": "error", "message": str(e)}


def parse_post_text(text):
    """Matnni sarlavha va asosiy mazmunga ajratish."""
    if not text:
        return "19-maktab yangiligi", ""

    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    if not lines:
        return "19-maktab yangiligi", text

    # Birinchi qator — Sarlavha
    title = lines[0]
    # Agar sarlavha juda uzun bo'lsa (120 belgidan ortiq), qisqartirish
    if len(title) > 120:
        first_sentence = title.split('.')[0]
        if len(first_sentence) < 120:
            title = first_sentence
        else:
            title = title[:115] + "..."

    # Qolgan barcha matn — To'liq mazmun
    content = text.strip()
    return title, content


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
            "Men uni darhol maktabning rasmiy veb-saytiga joylayman! 🚀"
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
            status_text = f"🟡 <b>Sayt yuklanmoqda...</b>\n{e}"
        send_telegram_message(chat_id, status_text)
        return

    # Yangilik qo'shish jarayoni
    send_telegram_message(chat_id, "⏳ <i>Yangilik qabul qilindi, saytga joylanmoqda...</i>")

    cover_bytes = None
    cover_filename = "cover.jpg"

    # Agar rasm yuborilgan bo'lsa
    if photos:
        # Eng katta sifatdagi rasm oxirida turadi
        best_photo = photos[-1]
        file_id = best_photo["file_id"]
        cover_bytes, cover_filename = get_file_bytes(file_id)

    title, content = parse_post_text(text)

    # Agar matn umuman bo'lmasa, lekin rasm bo'lsa
    if not text:
        title = f"19-maktab hayotidan fotolavha ({time.strftime('%d.%m.%Y')})"
        content = "Namangan tumani 19-sonli umumiy o'rta ta'lim maktabida o'tkazilgan tadbirlar va dars jarayonidan fotolavha."

    res = publish_to_website(title, content, cover_bytes, cover_filename)

    if res.get("status") == "ok":
        news_url = res.get("url") or f"{LIVE_SITE_URL}/news/{res.get('slug')}/"
        reply_msg = (
            "✅ <b>Yangilik saytga muvaffaqiyatli joylandi!</b>\n\n"
            f"📌 <b>Sarlavha:</b> {title}\n"
            f"📅 <b>Sana:</b> {time.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"🔗 <b>Saytda ko'rish:</b>\n{news_url}"
        )
        markup = {
            "inline_keyboard": [
                [{"text": "👀 Yangilikni ko'rish", "url": news_url}],
                [{"text": "🌐 Bosh sahifa", "url": LIVE_SITE_URL}]
            ]
        }
        send_telegram_message(chat_id, reply_msg, markup)
        print(f"[OK] Yangilik saytga joylandi: {title}")
    else:
        err = res.get("message", "Noma'lum xatolik")
        send_telegram_message(chat_id, f"❌ <b>Xatolik yuz berdi:</b> {err}\n\nIltimos, qaytadan urinib ko'ring.")
        print(f"[XATO] Joylashda xato: {err}")


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

    # Fon uyg'otuvchi robotni alohida thread'da ishga tushiramiz
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
                print("[OGOHLANTIRISH] Boshqa bot sessiyasi bor, 5 soniya kutilmoqda...")
                time.sleep(5)
        except requests.exceptions.RequestException:
            time.sleep(3)
        except Exception as e:
            print(f"[KUTILMAGAN XATO] {e}")
            time.sleep(3)


if __name__ == "__main__":
    run_bot()
