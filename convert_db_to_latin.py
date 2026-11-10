import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.news.models import News, NewsCategory

# Lotin alifbosiga o'girish qoidalari
CYR_TO_LAT_MAP = {
    'А': 'A', 'а': 'a',
    'Б': 'B', 'б': 'b',
    'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g',
    'Д': 'D', 'д': 'd',
    'Е': 'E', 'е': 'e',
    'Ё': 'Yo', 'ё': 'yo',
    'Ж': 'J', 'ж': 'j',
    'З': 'Z', 'з': 'z',
    'И': 'I', 'и': 'i',
    'Й': 'Y', 'й': 'y',
    'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l',
    'М': 'M', 'м': 'm',
    'Н': 'N', 'н': 'n',
    'О': 'O', 'о': 'o',
    'П': 'P', 'п': 'p',
    'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's',
    'Т': 'T', 'т': 't',
    'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f',
    'Х': 'X', 'х': 'x',
    'Ц': 'Ts', 'ц': 'ts',
    'Ч': 'Ch', 'ч': 'ch',
    'Ш': 'Sh', 'ш': 'sh',
    'Щ': 'Sh', 'щ': 'sh',
    'Ъ': "'", 'ъ': "'",
    'Ы': 'I', 'ы': 'i',
    'Ь': '', 'ь': '',
    'Э': 'E', 'э': 'e',
    'Ю': 'Yu', 'ю': 'yu',
    'Я': 'Ya', 'я': 'ya',
    'Ў': "O‘", 'ў': "o‘",
    'Қ': 'Q', 'қ': 'q',
    'Ғ': "G‘", 'ғ': "g‘",
    'Ҳ': 'H', 'ҳ': 'h',
}

def cyrillic_to_latin(text):
    if not text:
        return text

    # So'z boshidagi Ye/ye holatlari
    res = []
    i = 0
    length = len(text)
    while i < length:
        ch = text[i]
        prev_ch = text[i-1] if i > 0 else ' '
        
        # So'z boshida yoki unlidan keyin 'Е' / 'е' -> 'Ye' / 'ye'
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
    # Qo'shtirnoq va tutuq belgilarini standartlashtirish
    converted = converted.replace('`', "'").replace('’', "'").replace('ʻ', "‘").replace('ʼ', "‘")
    return converted

def run_conversion():
    updated_news = 0
    for n in News.objects.all():
        old_title = n.title
        new_title = cyrillic_to_latin(n.title)
        new_excerpt = cyrillic_to_latin(n.excerpt)
        new_content = cyrillic_to_latin(n.content)

        if old_title != new_title or n.content != new_content:
            n.title = new_title
            n.excerpt = new_excerpt
            n.content = new_content
            n.save(update_fields=['title', 'excerpt', 'content'])
            updated_news += 1
            print(f"[{n.id}] {old_title[:45]} -> {new_title[:45]}")

    print(f"\nJami yangilangan postlar: {updated_news} ta.")

if __name__ == '__main__':
    run_conversion()
