import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.news.models import News, NewsCategory
from apps.core.models import SiteSettings

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
    """
    O'zbek yangi lotin alifbosi:
    sh -> ş, Sh -> Ş
    ch -> ç, Ch -> Ç
    o', oʻ, o‘ -> ó, O', Oʻ, O‘ -> Ó
    g', gʻ, g‘ -> ğ, G', Gʻ, G‘ -> Ğ
    """
    if not text:
        return text

    # Agar kirillcha harflar bo'lsa avval o'giramiz
    text = cyrillic_to_latin(text)

    def convert_plain(t):
        # 1. G' va O' harflari
        t = re.sub(r"G[‘ʻ'`]", "Ğ", t)
        t = re.sub(r"g[‘ʻ'`]", "ğ", t)
        t = re.sub(r"O[‘ʻ'`]", "Ó", t)
        t = re.sub(r"o[‘ʻ'`]", "ó", t)

        # 2. CH / Ch / ch
        t = re.sub(r"CH\b", "Ç", t)
        t = re.sub(r"Ch", "Ç", t)
        t = re.sub(r"ch", "ç", t)

        # 3. SH / Sh / sh
        t = re.sub(r"SH\b", "Ş", t)
        t = re.sub(r"Sh", "Ş", t)
        t = re.sub(r"sh", "ş", t)

        return t

    # HTML teglari ichidagi matnlarni buzmaslik uchun ajratamiz
    parts = re.split(r'(<[^>]+>)', text)
    new_parts = []
    for part in parts:
        if part.startswith('<') and part.endswith('>'):
            new_parts.append(part)
        else:
            new_parts.append(convert_plain(part))

    return "".join(new_parts)

def update_all_database():
    print("Yangi o'zbek lotin alifbosi (ş, ç, ğ, ó) ga o'tkazilmoqda...")

    # 1. Kategoriyalar
    for cat in NewsCategory.objects.all():
        old_n = cat.name
        cat.name = to_new_uzbek_reform(cat.name)
        cat.save(update_fields=['name'])
        print(f"Kategoriya: {old_n} -> {cat.name}")

    # 2. Yangiliklar
    count = 0
    for n in News.objects.all():
        n.title = to_new_uzbek_reform(n.title)
        n.excerpt = to_new_uzbek_reform(n.excerpt)
        n.content = to_new_uzbek_reform(n.content)
        n.save(update_fields=['title', 'excerpt', 'content'])
        count += 1

    print(f"Barcha {count} ta yangilik yangi lotin alifbosiga o'tkazildi.")

    # 3. Sayt sozlamalari va direktor murojaati
    s = SiteSettings.objects.first()
    if s:
        s.director_name = "Nabiyeva Muyassarxon Nizomjonovna"
        s.director_message = (
            "Assalomu alaykum, aziz óquvçilar, hurmatli ota-onalar va ustozlar!\n\n"
            "19-umumiy órta ta'lim maktabimiz har bir farzandning orzu-intilişlarini róyobga çiqaruvçi, "
            "zamonaviy bilim va milliy tarbiya beruvçi qutluğ ziyo maskanidir.\n\n"
            "Bizning baş maqsadimiz — zamonaviy texnologiyalarni puxta egallagan, keng dunyoqaraşli, "
            "yuksak ma'naviyatli va ona Vatanimiz ravnaqiga munosib hissa qóşadigan barkamol avlodni "
            "tarbiyalab voyaga yetkazişdir. Maktabimiz eşiklari ilmga çanqoq barça yoşlar uçun hamişa oçiq!"
        )
        s.save()
        print("Direktor murojaati yangi alifboda saqlandi.")

if __name__ == '__main__':
    update_all_database()
