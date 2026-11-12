import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone
from apps.news.models import News, NewsCategory, NewsImage, NewsVideo

CYR_TO_LAT_MAP = {
    'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g', 'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e',
    'Ё': 'Yo', 'ё': 'yo', 'Ж': 'J', 'ж': 'j', 'З': 'Z', 'з': 'z',
    'И': 'I', 'и': 'i', 'Й': 'Y', 'й': 'y', 'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l', 'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n',
    'О': 'O', 'о': 'o', 'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's', 'Т': 'T', 'т': 't', 'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f', 'Х': 'X', 'х': 'x', 'Ц': 'Ts', 'ц': 'ts',
    'Ч': 'Ç', 'ч': 'ç', 'Ш': 'Ş', 'ш': 'ş', 'Щ': 'Ş', 'щ': 'ş',
    'Ъ': "'", 'ъ': "'", 'Ы': 'I', 'ы': 'i', 'Ь': '', 'ь': '',
    'Э': 'E', 'э': 'e', 'Ю': 'Yu', 'ю': 'yu', 'Я': 'Ya', 'я': 'ya',
    'Ў': "Ó", 'ў': "ó", 'Қ': 'Q', 'қ': 'q', 'Ғ': "Ğ", 'ғ': "ğ",
    'Ҳ': 'H', 'ҳ': 'h',
}

def cyrillic_to_latin(text):
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
    return "".join(res)

def to_new_uzbek_reform(text):
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

def get_or_create_category(name, color='#2563EB'):
    slug = slugify(name)
    cat, _ = NewsCategory.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'color': color}
    )
    return cat

def detect_category(text):
    t = text.lower()
    if any(k in t for k in ['olimpiada', 'g‘olib', "g'olib", 'ğolib', 'faxrli', 'yutuq', 'diplom', 'tabrik', 'sovrin', 'taqdirlandi']):
        return get_or_create_category('Yutuqlar va Olimpiadalar', '#F59E0B')
    if any(k in t for k in ['kelajak soati', 'dars', 'sinf', "o'qituvchi", "óqituvçi", 'mashg‘ulot', 'metod', 'seminar']):
        return get_or_create_category("Óquv jarayoni va darslar", '#10B981')
    if any(k in t for k in ['tadbir', 'bayram', 'suhbat', 'haftalik', 'mehr bilan', 'xotira', 'ma’naviyat', "ma'naviyat", 'konkurs', 'tanlov', 'uchrashuv', 'uçraşuv']):
        return get_or_create_category("Ma'naviyat va ma'rifat", '#8B5CF6')
    return get_or_create_category("Maktab yangiliklari", '#2563EB')

def clean_post_text(raw_text):
    if not raw_text:
        return "19-maktab hayotidan fotolavha", "<p>Namangan tumani 19-sonli umumiy órta ta'lim maktabi faoliyatidan lavha.</p>"

    lines = [line.strip() for line in raw_text.strip().split('\n') if line.strip()]
    if not lines:
        return "19-maktab hayotidan fotolavha", f"<p>{raw_text}</p>"

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

    content = "\n".join(paragraphs) if paragraphs else f"<p>{raw_text}</p>"
    return title.strip(), content

def sync_new_channel_posts():
    url = 'https://t.me/s/maktab19_rasmiy'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    print(f"Kanalga ulanilmoqda: {url}...")
    resp = requests.get(url, headers=headers, timeout=25)
    if resp.status_code != 200:
        print(f"Xato: status kodi {resp.status_code}")
        return

    soup = BeautifulSoup(resp.text, 'html.parser')
    messages = soup.find_all('div', class_='tgme_widget_message')
    print(f"Topilgan so'nggi xabarlar soni: {len(messages)}")

    new_added = 0
    for msg in messages:
        data_post = msg.get('data-post')
        if not data_post:
            continue
        num_str = data_post.split('/')[-1]
        if not num_str.isdigit():
            continue
        num = int(num_str)

        # Bazada bormi?
        if News.objects.filter(slug__startswith=f"post-{num}").exists():
            continue

        text_div = msg.find('div', class_='tgme_widget_message_text')
        raw_text = text_div.get_text(separator="\n").strip() if text_div else ""
        
        # Rasmlarni yig'ish
        photos = []
        for a in msg.find_all('a', class_='tgme_widget_message_photo_wrap'):
            style = a.get('style', '')
            m = re.search(r"background-image:url\('([^']+)'\)", style)
            if m:
                photos.append(m.group(1))

        # Videolarni yig'ish
        vid_src = None
        vid_tag = msg.find('video')
        if vid_tag and vid_tag.get('src'):
            vid_src = vid_tag['src']

        # Vaqt
        time_tag = msg.find('time')
        dt_str = time_tag.get('datetime') if time_tag else None

        if not raw_text and not photos and not vid_src:
            continue
        if len(raw_text) < 15 and not photos and not vid_src:
            continue

        title, content = clean_post_text(raw_text)
        title = to_new_uzbek_reform(title)
        content = to_new_uzbek_reform(content)

        pub_date = timezone.now()
        if dt_str:
            try:
                dt_obj = datetime.fromisoformat(dt_str)
                pub_date = timezone.make_aware(dt_obj) if timezone.is_naive(dt_obj) else dt_obj
            except Exception:
                pass

        category = detect_category(raw_text)
        clean_text = re.sub(r'<[^>]+>', '', content)
        excerpt = clean_text[:240].strip() + ('...' if len(clean_text) > 240 else '')

        slug = f"post-{num}-{slugify(title)[:60]}"
        idx = 1
        while News.objects.filter(slug=slug).exists():
            slug = f"post-{num}-{slugify(title)[:55]}-{idx}"
            idx += 1

        news_item = News(
            title=title,
            slug=slug,
            category=category,
            excerpt=excerpt,
            content=content,
            status='published',
            published_at=pub_date,
            is_featured=True,
            views_count=20
        )

        # 1-rasm: cover
        if photos:
            try:
                r_img = requests.get(photos[0], timeout=20, headers=headers)
                if r_img.status_code == 200 and len(r_img.content) > 1000:
                    news_item.cover_image.save(f"maktab19_{num}_cover.jpg", ContentFile(r_img.content), save=False)
            except Exception as e:
                print(f"  [Muqova yuklanmadi]: {e}")

        news_item.save()

        # Qo'shimcha galereya rasmlari
        if len(photos) > 1:
            for p_idx, p_url in enumerate(photos[1:8]):
                try:
                    r_p = requests.get(p_url, timeout=20, headers=headers)
                    if r_p.status_code == 200 and len(r_p.content) > 1000:
                        img_obj = NewsImage(news=news_item, order=p_idx + 1)
                        img_obj.image.save(f"maktab19_{num}_g_{p_idx+1}.jpg", ContentFile(r_p.content), save=True)
                except Exception as e:
                    print(f"  [Galereya rasmi yuklanmadi]: {e}")

        # Video mavjud bo'lsa
        if vid_src:
            try:
                r_v = requests.get(vid_src, timeout=40, headers=headers)
                if r_v.status_code == 200 and len(r_v.content) > 5000:
                    vid_obj = NewsVideo(news=news_item, title=f"{title[:90]} (Videolavha)")
                    vid_obj.video_file.save(f"maktab19_{num}_video.mp4", ContentFile(r_v.content), save=True)
            except Exception as e:
                print(f"  [Video yuklanmadi]: {e}")

        new_added += 1
        print(f"✅ Yangi post #{num} joylandi: {title[:65]} (Rasmlar: {len(photos)})")

    print("=" * 60)
    print(f"Jami yangi qo'shilgan yangiliklar: {new_added} ta.")
    print(f"Bazada jami yangiliklar soni: {News.objects.count()} ta.")
    print("=" * 60)

if __name__ == '__main__':
    sync_new_channel_posts()
