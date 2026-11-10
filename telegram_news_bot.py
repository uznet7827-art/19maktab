"""
19-Maktab — Telegram Yangiliklar & Avto-Sinxronizatsiya Boti
============================================================
1. Botga yuborilgan rasm, video va matnlarni to'g'ridan-to'g'ri maktab saytiga yangilik qilib joylaydi.
2. Yangi o'zbek lotin alifbosi qoidalariga to'liq moslashtiradi (kirillcha matnlarni lotinchaga o'giradi).
3. @maktab19_rasmiy kanalini doimiy kuzatib boradi: yangi post yoki video chiqsa,
   avtomatik ravishda rasmlari/videolari bilan saytga joylaydi.
4. Sayt uxlab qolmasligi uchun fon rejimida har 5 daqiqada uyg'otib turadi (Keep-Alive).
"""

import os
import sys
import time
import re
import uuid
import threading
import requests
from io import BytesIO
from datetime import datetime
from bs4 import BeautifulSoup

# Django muhitini yuklaymiz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone
from apps.news.models import News, NewsCategory, NewsImage, NewsVideo

BOT_TOKEN = "8864775756:AAECLlA465NwQR0E-93CYy07HPiuSs2B7Ko"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
CHANNEL_URL = "https://t.me/s/maktab19_rasmiy"

# Jonli sayt manzillari
LIVE_SITE_URL = "https://one9maktab-nmg.onrender.com"
HEALTH_ENDPOINT = f"{LIVE_SITE_URL}/health/"

# Admin Telegram ID lar to'plami
ADMIN_CHAT_IDS = set()


# Yangi lotin alifbosi transliteratsiyasi
CYR_TO_LAT_MAP = {
    'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g', 'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e',
    'Ё': 'Yo', 'ё': 'yo', 'Ж': 'J', 'ж': 'j', 'З': 'Z', 'з': 'z',
    'И': 'I', 'и': 'i', 'Й': 'Y', 'й': 'y', 'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l', 'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n',
    'О': 'O', 'о': 'o', 'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's', 'Т': 'T', 'т': 't', 'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f', 'Х': 'X', 'х': 'x', 'Ц': 'Ts', 'ц': 'ts',
    'Ч': 'Ch', 'ч': 'ch', 'Ш': 'Sh', 'ш': 'sh', 'Щ': 'Sh', 'щ': 'sh',
    'Ъ': "'", 'ъ': "'", 'Ы': 'I', 'ы': 'i', 'Ь': '', 'ь': '',
    'Э': 'E', 'э': 'e', 'Ю': 'Yu', 'ю': 'yu', 'Я': 'Ya', 'я': 'ya',
    'Ў': "O‘", 'ў': "o‘", 'Қ': 'Q', 'қ': 'q', 'Ғ': "G‘", 'ғ': "g‘",
    'Ҳ': 'H', 'ҳ': 'h',
}

def to_new_uzbek_reform(text):
    """O'zbek yangi lotin alifbosi: sh->ş, ch->ç, o'->ó, g'->ğ"""
    if not text:
        return text
    text = cyrillic_to_latin(text)
    def convert_plain(t):
        t = re.sub(r"G[‘ʻ'`]", "Ğ", t)
        t = re.sub(r"g[‘ʻ'`]", "ğ", t)
        t = re.sub(r"O[‘ʻ'`]", "Ó", t)
        t = re.sub(r"o[‘ʻ'`]", "ó", t)
        t = re.sub(r"CH\b", "Ç", t)
        t = re.sub(r"Ch", "Ç", t)
        t = re.sub(r"ch", "ç", t)
        t = re.sub(r"SH\b", "Ş", t)
        t = re.sub(r"Sh", "Ş", t)
        t = re.sub(r"sh", "ş", t)
        return t
    parts = re.split(r'(<[^>]+>)', text)
    new_parts = [p if (p.startswith('<') and p.endswith('>')) else convert_plain(p) for p in parts]
    return "".join(new_parts)


def cyrillic_to_latin(text):
    """Kirill yozuvidagi matnni zamonaviy o'zbek lotin alifbosiga o'tkazish."""
    if not text:
        return text
    res = []
    i = 0
    length = len(text)
    while i < length:
        ch = text[i]
        prev_ch = text[i-1] if i > 0 else ' '
        if ch in ('Е', 'е'):
            is_word_start = (i == 0 or prev_ch in ' \n\t.,;:!?"\'«»-–—')
            is_after_vowel = prev_ch.upper() in 'АЕЁИОУЭЮЯЎAEOIU'
            if is_word_start or is_after_vowel:
                res.append('Ye' if ch == 'Е' else 'ye')
            else:
                res.append('E' if ch == 'Е' else 'e')
        elif ch in CYR_TO_LAT_MAP:
            res.append(CYR_TO_LAT_MAP[ch])
        else:
            res.append(ch)
        i += 1
    converted = "".join(res)
    return converted.replace('`', "'").replace('’', "'").replace('ʻ', "‘").replace('ʼ', "‘")


def send_telegram_message(chat_id, text, reply_markup=None):
    """Foydalanuvchiga Telegram xabari yuborish."""
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[TG XATOSI] {e}")


def get_file_bytes(file_id):
    """Telegram serveridan fayl (rasm/video) yuklab olish."""
    try:
        f_info = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}", timeout=15).json()
        if f_info.get("ok"):
            file_path = f_info["result"]["file_path"]
            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            resp = requests.get(download_url, timeout=45)
            if resp.status_code == 200:
                ext = file_path.split('.')[-1] if '.' in file_path else 'jpg'
                return resp.content, f"{uuid.uuid4().hex[:8]}.{ext}"
    except Exception as e:
        print(f"[YUKLASH XATOSI] Fayl yuklanmadi: {e}")
    return None, None


def get_or_create_category(name, color='#2563EB'):
    slug = slugify(name)
    cat, _ = NewsCategory.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'color': color}
    )
    return cat


def detect_category_for_text(text):
    t = text.lower()
    if any(k in t for k in ['olimpiada', 'g‘olib', "g'olib", 'faxrli', 'yutuq', 'diplom', 'tabrik', 'sovrin', 'taqdirlandi']):
        return get_or_create_category('Yutuqlar va Olimpiadalar', '#F59E0B')
    if any(k in t for k in ['kelajak soati', 'dars', 'sinf', "o'qituvchi", 'mashg‘ulot', 'metod', 'seminar']):
        return get_or_create_category("O'quv jarayoni va darslar", '#10B981')
    if any(k in t for k in ['tadbir', 'bayram', 'suhbat', 'haftalik', 'mehr bilan', 'xotira', 'ma’naviyat', "ma'naviyat", 'konkurs', 'tanlov', 'uchrashuv']):
        return get_or_create_category("Ma'naviyat va ma'rifat", '#8B5CF6')
    return get_or_create_category("Maktab yangiliklari", '#2563EB')


def parse_post_text(text):
    """Matnni tozalab, lotin alifbosidagi sarlavha va HTML formatli mazmunga ajratish."""
    text = to_new_uzbek_reform(text or "")
    if not text.strip():
        return "19-maktab hayotidan yangilik", "<p>Namangan tumani 19-sonli umumiy o'rta ta'lim maktabi faoliyatidan lavha.</p>"

    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    if not lines:
        return "19-maktab hayotidan yangilik", f"<p>{text}</p>"

    first_line = re.sub(r'^[•\-\–\—\*\s]+', '', lines[0])
    if len(first_line) > 130:
        sentences = re.split(r'[\.\!\?]\s+', first_line)
        title = sentences[0] if len(sentences[0]) < 130 else first_line[:125] + "..."
    else:
        title = first_line

    paragraphs = []
    for line in lines:
        if line.startswith('http://') or line.startswith('https://') or line.startswith('t.me/'):
            continue
        if line.startswith('#'):
            continue
        paragraphs.append(f"<p>{line}</p>")

    content = "\n".join(paragraphs) if paragraphs else f"<p>{text}</p>"
    return title.strip(), content


def save_news_to_django(title, content, cover_bytes=None, cover_filename=None, category=None, post_num=None, gallery_bytes_list=None, video_bytes=None, video_filename=None):
    """Yangilik, rasmlar va videolarni Django bazasiga saqlash."""
    title = to_new_uzbek_reform(title)
    content = to_new_uzbek_reform(content)

    if not category:
        category = detect_category_for_text(title + " " + content)

    if post_num:
        base_slug = f"post-{post_num}-{slugify(title)[:60]}"
    else:
        base_slug = slugify(title)[:70] or f"news-{uuid.uuid4().hex[:8]}"

    slug = base_slug
    counter = 1
    while News.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    clean_text = re.sub(r'<[^>]+>', '', content)
    excerpt = clean_text[:240].strip() + ('...' if len(clean_text) > 240 else '')

    news_item = News(
        title=title,
        slug=slug,
        category=category,
        excerpt=excerpt,
        content=content,
        status='published',
        published_at=timezone.now(),
        is_featured=True,
        views_count=25
    )

    if cover_bytes:
        news_item.cover_image.save(cover_filename or "cover.jpg", ContentFile(cover_bytes), save=False)

    news_item.save()

    # Galereya rasmlarini qo'shish
    if gallery_bytes_list:
        for idx, (img_bytes, img_name) in enumerate(gallery_bytes_list):
            img_obj = NewsImage(news=news_item, order=idx + 1)
            img_obj.image.save(img_name, ContentFile(img_bytes), save=True)

    # Video faylini qo'shish
    if video_bytes:
        vid_obj = NewsVideo(
            news=news_item,
            title=f"{title[:90]} (Videolavha)"
        )
        vid_obj.video_file.save(video_filename or "video.mp4", ContentFile(video_bytes), save=True)

    return news_item


def handle_update(update):
    """Telegram yangilanishini qayta ishlash."""
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    ADMIN_CHAT_IDS.add(chat_id)

    text = message.get("text") or message.get("caption") or ""
    photos = message.get("photo")
    video = message.get("video") or message.get("video_note") or message.get("animation")

    # /start buyrug'i
    if text.strip().startswith("/start"):
        start_msg = (
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "Bu <b>19-sonli maktabning rasmiy yangiliklar va media boti</b>.\n\n"
            "🌟 <b>Imkoniyatlar:</b>\n"
            "• Menga <b>rasm</b> yoki <b>video</b> va uning matnini yuborsangiz — darhol maktab saytiga yangilik qilib joylayman!\n"
            "• Barcha matnlar avtomatik tarzda <b>yangi lotin alifbosi</b> qoidalariga moslashtiriladi.\n"
            "• <b>@maktab19_rasmiy</b> kanalidagi yangi postlar avtomatik tarzda saytga o'tib boradi!\n"
            "• Sayt serveri doimiy uyg'oq (faol) holatda ushlab turiladi. 🚀"
        )
        markup = {
            "inline_keyboard": [
                [{"text": "🌐 Saytni ochish", "url": LIVE_SITE_URL}],
                [{"text": "📰 Yangiliklar", "url": f"{LIVE_SITE_URL}/news/"}]
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
            db_news_count = News.objects.count()
            status_text = (
                f"🟢 <b>Sayt to'liq faol va uyg'oq!</b>\n\n"
                f"⏱ Javob vaqti: <b>{elapsed} ms</b>\n"
                f"📰 Saytdagi jami yangiliklar: <b>{db_news_count} ta</b>\n"
                f"📡 @maktab19_rasmiy kanali: <b>Ulangan (Avto-sinxron)</b>\n"
                f"🔤 Yozuv tizimi: <b>Yangi o'zbek lotin alifbosi</b>\n\n"
                f"🔗 {LIVE_SITE_URL}"
            )
        except Exception as e:
            status_text = f"🟡 <b>Sayt tekshirilmoqda...</b>\n{e}"
        send_telegram_message(chat_id, status_text)
        return

    # Yangilik / Media qo'shish
    send_telegram_message(chat_id, "⏳ <i>Media qabul qilindi, yangi lotin alifbosida saytga joylanmoqda...</i>")

    cover_bytes = None
    cover_filename = "cover.jpg"
    video_bytes = None
    video_filename = "video.mp4"

    # Rasm mavjud bo'lsa
    if photos:
        best_photo = photos[-1]
        file_id = best_photo["file_id"]
        cover_bytes, cover_filename = get_file_bytes(file_id)

    # Video mavjud bo'lsa
    if video:
        v_file_id = video["file_id"]
        video_bytes, video_filename = get_file_bytes(v_file_id)
        # Agar rasm bo'lmasa, videoning thumb rasmiga urinib ko'ramiz
        if not cover_bytes and video.get("thumbnail"):
            cover_bytes, cover_filename = get_file_bytes(video["thumbnail"]["file_id"])

    title, content = parse_post_text(text)

    if not text:
        if video_bytes:
            title = f"19-maktab hayotidan videolavha ({time.strftime('%d.%m.%Y')})"
            content = "<p>Namangan tumani 19-sonli maktab faoliyatidan maxsus videolavha.</p>"
        elif cover_bytes:
            title = f"19-maktab hayotidan fotolavha ({time.strftime('%d.%m.%Y')})"
            content = "<p>Namangan tumani 19-sonli umumiy o'rta ta'lim maktabi tadbirlaridan fotolavha.</p>"

    try:
        news_item = save_news_to_django(
            title=title,
            content=content,
            cover_bytes=cover_bytes,
            cover_filename=cover_filename,
            video_bytes=video_bytes,
            video_filename=video_filename
        )
        news_url = f"{LIVE_SITE_URL}{news_item.get_absolute_url()}"

        media_icon = "📹" if video_bytes else "📸"
        reply_msg = (
            f"✅ <b>{media_icon} Yangilik saytga muvaffaqiyatli joylandi!</b>\n\n"
            f"📌 <b>Sarlavha:</b> {news_item.title}\n"
            f"📂 <b>Toifa:</b> {news_item.category.name if news_item.category else 'Maktab'}\n"
            f"📅 <b>Sana:</b> {news_item.published_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"🔗 <b>Havola:</b> {news_url}"
        )
        markup = {
            "inline_keyboard": [
                [{"text": "👀 Yangilikni ko'rish", "url": news_url}],
                [{"text": "🌐 Saytga o'tish", "url": LIVE_SITE_URL}]
            ]
        }
        send_telegram_message(chat_id, reply_msg, markup)
        print(f"[OK] Media yangilik saqlandi: {news_item.title} ({news_item.slug})")
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


def sync_channel_daemon():
    """@maktab19_rasmiy kanalini doimiy kuzatib, yangi post va videolarni avtomatik saytga joylaydi."""
    time.sleep(15)
    print("[KANAL KUZATUVCHI] @maktab19_rasmiy kanali nazorati faol.")

    while True:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(CHANNEL_URL, headers=headers, timeout=20)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                messages = soup.find_all('div', class_='tgme_widget_message')
                for msg in reversed(messages):
                    post_id = msg.get('data-post')
                    if not post_id or '/' not in post_id:
                        continue
                    num_str = post_id.split('/')[-1]
                    if not num_str.isdigit():
                        continue
                    num = int(num_str)

                    # Baza tekshirish
                    if News.objects.filter(slug__startswith=f"post-{num}").exists():
                        continue

                    text_div = msg.find('div', class_='tgme_widget_message_text')
                    text = text_div.get_text(separator="\n").strip() if text_div else ""

                    # Rasmlar
                    photo_links = []
                    for a in msg.find_all('a', class_='tgme_widget_message_photo_wrap'):
                        style = a.get('style', '')
                        m = re.search(r"background-image:url\('([^']+)'\)", style)
                        if m:
                            photo_links.append(m.group(1))

                    # Videolarni tekshirish
                    video_link = None
                    vid_tag = msg.find('video')
                    if vid_tag and vid_tag.get('src'):
                        video_link = vid_tag['src']

                    if not text and not photo_links and not video_link:
                        continue
                    if len(text) < 15 and not photo_links and not video_link:
                        continue

                    title, content = parse_post_text(text)
                    category = detect_category_for_text(title + " " + text)

                    # 1-rasm: cover
                    cover_bytes = None
                    cover_name = f"maktab19_{num}_cover.jpg"
                    if photo_links:
                        r_img = requests.get(photo_links[0], timeout=20, headers=headers)
                        if r_img.status_code == 200 and len(r_img.content) > 1000:
                            cover_bytes = r_img.content

                    # Galereya rasmlari
                    gallery_list = []
                    if len(photo_links) > 1:
                        for g_idx, g_url in enumerate(photo_links[1:8]):
                            r_g = requests.get(g_url, timeout=20, headers=headers)
                            if r_g.status_code == 200 and len(r_g.content) > 1000:
                                gallery_list.append((r_g.content, f"maktab19_{num}_g_{g_idx+1}.jpg"))

                    # Video fayli
                    video_bytes = None
                    video_name = f"maktab19_{num}_video.mp4"
                    if video_link:
                        try:
                            r_v = requests.get(video_link, timeout=40, headers=headers)
                            if r_v.status_code == 200 and len(r_v.content) > 5000:
                                video_bytes = r_v.content
                        except Exception:
                            pass

                    news_item = save_news_to_django(
                        title=title,
                        content=content,
                        cover_bytes=cover_bytes,
                        cover_filename=cover_name,
                        category=category,
                        post_num=num,
                        gallery_bytes_list=gallery_list,
                        video_bytes=video_bytes,
                        video_filename=video_name
                    )
                    print(f"[KANAL -> SAYT] Yangi post/video saytga joylandi: #{num} - {news_item.title}")

                    # Adminlarga bildirishnoma yuborish
                    for c_id in list(ADMIN_CHAT_IDS):
                        notif = (
                            "📢 <b>@maktab19_rasmiy kanalidan yangi yangilik saytga joylandi!</b>\n\n"
                            f"📌 <b>Sarlavha:</b> {news_item.title}\n"
                            f"🔗 {LIVE_SITE_URL}{news_item.get_absolute_url()}"
                        )
                        send_telegram_message(c_id, notif)
        except Exception as e:
            print(f"[KANAL XATOSI] {e}")

        time.sleep(300)


def run_bot():
    """Telegram Botni doimiy eshitish (Polling) rejimida ishga tushirish."""
    print("=" * 65)
    print(" 19-Maktab Media & Yangiliklar Boti ishga tushdi!")
    print(f" Bot: @Xoldarxojayev_agent_ai_bot")
    print(f" Kanal: @maktab19_rasmiy")
    print(" Video, rasm va lotin alifbosi qo'llab-quvvatlanadi.")
    print("=" * 65)

    t_keep = threading.Thread(target=keep_alive_daemon, daemon=True)
    t_keep.start()

    t_sync = threading.Thread(target=sync_channel_daemon, daemon=True)
    t_sync.start()

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
