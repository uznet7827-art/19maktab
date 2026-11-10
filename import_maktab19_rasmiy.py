import os
import sys
import json
import re
import requests
from datetime import datetime
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone
from apps.news.models import News, NewsCategory, NewsImage

def setup_categories():
    categories = {
        'yutuqlar': {'name': 'Yutuqlar va Olimpiadalar', 'color': '#F59E0B'},
        'oquv': {'name': "O'quv jarayoni va darslar", 'color': '#10B981'},
        'manaviyat': {'name': "Ma'naviyat va ma'rifat", 'color': '#8B5CF6'},
        'maktab': {'name': "Maktab yangiliklari", 'color': '#2563EB'},
    }
    obj_map = {}
    for key, data in categories.items():
        slug = slugify(data['name'])
        cat, _ = NewsCategory.objects.get_or_create(
            slug=slug,
            defaults={'name': data['name'], 'color': data['color']}
        )
        obj_map[key] = cat
    return obj_map

def detect_category(text, cat_map):
    t = text.lower()
    if any(k in t for k in ['olimpiada', 'g‘olib', "g'olib", 'faxrli', 'yutuq', 'diplom', 'tabrik', 'sovrin', 'taqdirlandi']):
        return cat_map['yutuqlar']
    if any(k in t for k in ['kelajak soati', 'dars', 'sinf', "o'qituvchi", 'mashg‘ulot', 'metod', 'seminar']):
        return cat_map['oquv']
    if any(k in t for k in ['tadbir', 'bayram', 'suhbat', 'haftalik', 'mehr bilan', 'xotira', 'ma’naviyat', "ma'naviyat", 'konkurs', 'tanlov', 'uchrashuv']):
        return cat_map['manaviyat']
    return cat_map['maktab']

def clean_post_text(raw_text):
    if not raw_text:
        return "19-maktab hayotidan fotolavha", "<p>Namangan tumani 19-sonli umumiy o'rta ta'lim maktabi faoliyatidan lavhalar.</p>"

    # Clean redundant spaces and telegram specific links
    lines = [line.strip() for line in raw_text.strip().split('\n') if line.strip()]
    if not lines:
        return "19-maktab hayotidan fotolavha", "<p>Namangan tumani 19-sonli umumiy o'rta ta'lim maktabi yangiliklari.</p>"

    first_line = lines[0]
    # Remove leading dots, dashes, emojis from start of title
    first_line = re.sub(r'^[•\-\–\—\*\s]+', '', first_line)

    if len(first_line) > 130:
        sentences = re.split(r'[\.\!\?]\s+', first_line)
        title = sentences[0] if len(sentences[0]) < 130 else first_line[:125] + "..."
    else:
        title = first_line

    # Format content nicely into HTML paragraphs
    paragraphs = []
    for line in lines:
        if line.startswith('http://') or line.startswith('https://') or line.startswith('t.me/'):
            continue
        if line.startswith('#'):
            # hashtag
            continue
        paragraphs.append(f"<p>{line}</p>")

    content_html = "\n".join(paragraphs) if paragraphs else f"<p>{raw_text}</p>"
    return title.strip(), content_html

def download_image(url):
    try:
        r = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
    except Exception as e:
        print(f"  [Rasm yuklab olinmadi]: {e}")
    return None

def import_all_posts(limit=None):
    cat_map = setup_categories()

    with open(os.path.join(BASE_DIR, 'channel_posts.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Sort descending by num (newest first)
    posts = list(data.values())
    posts.sort(key=lambda p: p.get('num', 0), reverse=True)

    print(f"Jami skrap qilingan postlar: {len(posts)}")
    imported_count = 0

    for idx, post in enumerate(posts):
        num = post.get('num')
        raw_text = post.get('text', '') or ''
        photos = post.get('photos', [])
        dt_str = post.get('dt')

        # Filter out completely empty or purely service messages
        if not raw_text.strip() and not photos:
            continue
        if len(raw_text.strip()) < 15 and not photos:
            continue

        title, content = clean_post_text(raw_text)

        # Check if already exists by title or slug
        base_slug = f"post-{num}-{slugify(title)[:60]}"
        if News.objects.filter(slug__startswith=f"post-{num}").exists():
            print(f"[{num}] Allaqachon mavjud, o'tkazib yuborildi.")
            continue

        # Parse date
        pub_date = timezone.now()
        if dt_str:
            try:
                # e.g. 2026-11-03T07:12:00+00:00
                dt_obj = datetime.fromisoformat(dt_str)
                pub_date = timezone.make_aware(dt_obj) if timezone.is_naive(dt_obj) else dt_obj
            except Exception:
                pass

        category = detect_category(raw_text, cat_map)
        excerpt = re.sub(r'<[^>]+>', '', content)[:240].strip()
        if len(excerpt) >= 235:
            excerpt += "..."

        is_feat = (idx < 5)  # Make first 5 newest posts featured

        news = News(
            title=title,
            slug=base_slug,
            category=category,
            excerpt=excerpt,
            content=content,
            status='published',
            is_featured=is_feat,
            published_at=pub_date,
            views_count=15 + (num % 50)
        )

        # Download cover photo
        if photos:
            cover_data = download_image(photos[0])
            if cover_data:
                cover_name = f"maktab19_{num}_cover.jpg"
                news.cover_image.save(cover_name, ContentFile(cover_data), save=False)

        news.save()

        # Save extra photos as NewsImage gallery
        if len(photos) > 1:
            for p_idx, p_url in enumerate(photos[1:9]):  # max 8 gallery photos
                p_data = download_image(p_url)
                if p_data:
                    img_obj = NewsImage(news=news, order=p_idx + 1)
                    img_name = f"maktab19_{num}_g_{p_idx+1}.jpg"
                    img_obj.image.save(img_name, ContentFile(p_data), save=True)

        imported_count += 1
        print(f"[{imported_count}] #{num} ({pub_date.strftime('%Y-%m-%d')}): {title[:60]}... ({len(photos)} rasm)")

        if limit and imported_count >= limit:
            break

    print("\n" + "=" * 50)
    print(f"Muvaffaqiyatli import qilindi: {imported_count} ta yangilik!")
    print(f"Bazada jami yangiliklar: {News.objects.count()} ta.")
    print("=" * 50)

if __name__ == '__main__':
    import_all_posts()
