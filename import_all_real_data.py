import os
import sys
import json
import urllib.request
import django
from datetime import datetime, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.stdout.reconfigure(encoding='utf-8')
django.setup()

from apps.core.models import SiteSettings, Statistic, GalleryImage, SchoolHistory
from apps.news.models import News, NewsCategory
from apps.teachers.models import Teacher, Department
from apps.achievements.models import Achievement

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def download_image(url, rel_path):
    full_path = os.path.join(BASE_DIR, 'media', rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    if not os.path.exists(full_path) or os.path.getsize(full_path) == 0:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                with open(full_path, 'wb') as f:
                    f.write(resp.read())
            print(f"[Downloaded] {rel_path}")
        except Exception as e:
            print(f"[Failed] {rel_path}: {e}")
            return None
    return rel_path

print("--- 1. Updating SiteSettings ---")
site = SiteSettings.objects.first()
if not site:
    site = SiteSettings.objects.create(school_name="19-sonli umumiy o'rta ta'lim maktabi")

site.school_name = "19-sonli umumiy o'rta ta'lim maktabi"
site.school_name_ru = "Общеобразовательная школа №19"
site.school_name_en = "Secondary School #19"
site.tagline = "Sifatli ta'lim, yetakchi yoshlar va yorqin kelajak maktabi!"
site.address = "Namangan viloyati, Namangan tumani, 19-sonli umumiy o'rta ta'lim maktabi"
site.telegram_url = "https://t.me/qwert19idum"
site.save()
print("[OK] SiteSettings updated.")

print("\n--- 2. Creating Departments ---")
dept_lang, _ = Department.objects.get_or_create(name="Tillar kafedrasi", defaults={'name_ru': "Кафедра языков", 'name_en': "Department of Languages"})
dept_exact, _ = Department.objects.get_or_create(name="Aniq va tabiiy fanlar", defaults={'name_ru': "Точные науки", 'name_en': "Exact & Natural Sciences"})
dept_manaviy, _ = Department.objects.get_or_create(name="Ma'naviy-ma'rifiy va sport", defaults={'name_ru': "Духовно-просветительское и спорт", 'name_en': "Spiritual, Educational & Sports"})
dept_primary, _ = Department.objects.get_or_create(name="Boshlang'ich ta'lim", defaults={'name_ru': "Начальное образование", 'name_en': "Primary Education"})
dept_faxriy, _ = Department.objects.get_or_create(name="Faxriy ustozlar", defaults={'name_ru': "Почетные учителя", 'name_en': "Honorary Senior Teachers"})

# Load structured items
items = json.load(open('structured_items.json', encoding='utf-8'))

print("\n--- 3. Creating Real Teachers ---")
teachers_data = [
    {
        'full_name': "Mirxalova Mastura",
        'subject': "Rus tili va adabiyoti",
        'position': "Yetakchi o'qituvchi, 8-A va 11-A sinf rahbari",
        'department': dept_lang,
        'bio': "8-A va 11-A sinflari rahbari. Rus tili fanidan noan'anaviy darslar va 'Проектная работа' loyihalari tashkilotchisi.",
        'experience_years': 18,
        'order': 1,
        'photo_url': items[1]['photos'][0] if len(items[1]['photos']) > 0 else None,
        'rel_photo': "teachers/mastura_mirxalova.jpg"
    },
    {
        'full_name': "Narzullayeva G.",
        'subject': "Maktab maslahatchisi",
        'position': "Maktab maslahatchisi, O'quvchilar kengashi koordinatori",
        'department': dept_manaviy,
        'bio': "Maktabda 'Kelajak soati' va O'quvchilar kengashi yetakchilarini tayyorlash bo'yicha mas'ul mutaxassis.",
        'experience_years': 12,
        'order': 2,
        'photo_url': items[0]['photos'][0] if len(items[0]['photos']) > 0 and 'http' in items[0]['photos'][0] else None,
        'rel_photo': "teachers/g_narzullayeva.jpg"
    },
    {
        'full_name': "Shokirova M.",
        'subject': "MMIBDO'",
        'position': "Ma'naviy-ma'rifiy ishlar bo'yicha direktor o'rinbosari",
        'department': dept_manaviy,
        'bio': "Maktabning tarbiyaviy, ma'naviy-ma'rifiy jarayonlari va yoshlar tashabbuslarini muvofiqlashtiruvchi rahbar.",
        'experience_years': 15,
        'order': 3,
        'photo_url': items[3]['photos'][0] if len(items[3]['photos']) > 0 and 'http' in items[3]['photos'][0] else None,
        'rel_photo': "teachers/m_shokirova.jpg"
    },
    {
        'full_name': "Xamdamova S.",
        'subject': "Jismoniy tarbiya",
        'position': "Oliy toifali jismoniy tarbiya ustozi",
        'department': dept_manaviy,
        'bio': "Maktab sport jamoalari murabbiyi. 'Besh tashabbus' olimpiadasi shaxmat-shashka va sport musobaqalari bosh hakami.",
        'experience_years': 14,
        'order': 4,
        'photo_url': items[12]['photos'][0] if len(items[12]['photos']) > 0 and 'http' in items[12]['photos'][0] else None,
        'rel_photo': "teachers/s_xamdamova.jpg"
    },
    {
        'full_name': "Bekmirzayeva N.",
        'subject': "Maktab psixologi",
        'position': "Amaliyotchi psixolog",
        'department': dept_manaviy,
        'bio': "O'quvchilarning psixologik salomatligi, kasbga yo'naltirish va shaxsiy rivojlanishiga ko'maklashuvchi mutaxassis.",
        'experience_years': 10,
        'order': 5,
        'photo_url': items[3]['photos'][1] if len(items[3]['photos']) > 1 and 'http' in items[3]['photos'][1] else None,
        'rel_photo': "teachers/n_bekmirzayeva.jpg"
    },
    {
        'full_name': "Xasanova M.",
        'subject': "Xotin-qizlar masalalari",
        'position': "Xotin-qizlar masalalari bo'yicha mas'ul pedagog",
        'department': dept_manaviy,
        'bio': "Qizlar tarbiyasi, odob-axloq, kiyinish madaniyati va milliy qadriyatlarni targ'ib qiluvchi pedagog.",
        'experience_years': 16,
        'order': 6,
        'photo_url': None,
        'rel_photo': "teachers/m_xasanova.jpg"
    },
    {
        'full_name': "Ubaydullayeva M.",
        'subject': "Pedagogika, 11-B sinf rahbari",
        'position': "11-B sinf rahbari, Yetakchi ustoz",
        'department': dept_exact,
        'bio': "Bitiruvchi sinf o'quvchilarining oliy ta'limga yo'naltirilishi va kasb tanlashiga boshchilik qiluvchi ustoz.",
        'experience_years': 19,
        'order': 7,
        'photo_url': items[8]['photos'][0] if len(items[8]['photos']) > 0 and 'http' in items[8]['photos'][0] else None,
        'rel_photo': "teachers/m_ubaydullayeva.jpg"
    },
    {
        'full_name': "Ubaydullayev Hamidullo",
        'subject': "Ingliz tili (Faxriy)",
        'position': "Nafaqadagi faxriy ingliz tili o'qituvchisi",
        'department': dept_faxriy,
        'bio': "Ko'p yillar davomida yuzlab shogirdlarga chet tillarini o'rgatgan, maktabning eng hurmatli faxriy ustozlaridan biri.",
        'experience_years': 40,
        'order': 8,
        'photo_url': items[18]['photos'][0] if len(items[18]['photos']) > 0 and 'http' in items[18]['photos'][0] else None,
        'rel_photo': "teachers/hamidullo_ubaydullayev.jpg"
    },
    {
        'full_name': "Yunusova Gulbahor",
        'subject': "Boshlang'ich ta'lim (Faxriy)",
        'position': "Nafaqadagi faxriy ustoz",
        'department': dept_faxriy,
        'bio': "Maktabimizning faxriy o'qituvchisi, xalq ta'limi fidoyisi.",
        'experience_years': 38,
        'order': 9,
        'photo_url': items[16]['photos'][0] if len(items[16]['photos']) > 0 and 'http' in items[16]['photos'][0] else None,
        'rel_photo': "teachers/gulbahor_yunusova.jpg"
    },
]

for td in teachers_data:
    t_obj, _ = Teacher.objects.get_or_create(full_name=td['full_name'])
    t_obj.subject = td['subject']
    t_obj.position = td['position']
    t_obj.department = td['department']
    t_obj.bio = td['bio']
    t_obj.experience_years = td['experience_years']
    t_obj.is_active = True
    t_obj.is_featured = True
    t_obj.order = td['order']
    
    if td['photo_url']:
        downloaded = download_image(td['photo_url'], td['rel_photo'])
        if downloaded:
            t_obj.photo = downloaded
    t_obj.save()
    print(f"[OK] Teacher saved: {t_obj.full_name}")

print("\n--- 4. Creating Real Achievements ---")
# 1. Abdusattorova Nigora
ach1, _ = Achievement.objects.get_or_create(
    student_name="Abdusattorova Nigora",
    grade="6-A",
    title="Kelajak yulduzlari ochiq olimpiadasi — Super oliy o'rin!",
    defaults={
        'achievement_type': 'olympiad',
        'description': "Farg'ona viloyatida o'tkazilgan 'Kelajak yulduzlari ochiq olimpiadasi'da ingliz tili fanidan faxrli 'Super oliy' o'rinni egallab, maxsus sertifikat bilan taqdirlandi.",
        'date': date(2026, 10, 1),
        'place': "Super Oliy",
        'is_active': True,
        'parent_consent': True,
    }
)
if len(items[21]['photos']) > 0 and 'http' in items[21]['photos'][0]:
    p = download_image(items[21]['photos'][0], "achievements/nigora_abdusattorova.jpg")
    if p:
        ach1.photo = p
        ach1.save()

# 2. Besh tashabbus Yengil atletika
ach2, _ = Achievement.objects.get_or_create(
    student_name="19-maktab Yengil atletika jamoasi",
    grade="5-6 va 7-8 sinflar",
    title="Besh tashabbus Yengil atletika musobaqasi — 1-o'rin va tuman yo'llanmasi",
    defaults={
        'achievement_type': 'sport',
        'description': "Besh tashabbus olimpiadasi Yengil atletika musobaqasining 4-hudud bosqichida o'g'il bolalar va qizlar jamoalarimiz 1-o'rinni qo'lga kiritib, tuman bosqichiga yo'llanma oldi.",
        'date': date(2026, 10, 10),
        'place': "1-o'rin",
        'is_active': True,
        'parent_consent': True,
    }
)
if len(items[4]['photos']) > 0 and 'http' in items[4]['photos'][0]:
    p = download_image(items[4]['photos'][0], "achievements/yengil_atletika.jpg")
    if p:
        ach2.photo = p
        ach2.save()

# 3. Shaxmat-shashka
ach3, _ = Achievement.objects.get_or_create(
    student_name="19-maktab Shaxmat-shashka jamoasi",
    grade="5-11 sinf qizlar",
    title="Besh tashabbus Shaxmat-shashka olimpiadasi — 1-o'rin",
    defaults={
        'achievement_type': 'sport',
        'description': "Shaxmat-shashka 4-hudud musobaqalarida maktabimizning 5-11 sinf qizlar jamoasi 1-o'rinni, o'g'il bolalar jamoasi esa faxrli 2-o'rinni egalladi.",
        'date': date(2026, 10, 10),
        'place': "1-o'rin",
        'is_active': True,
        'parent_consent': True,
    }
)
if len(items[12]['photos']) > 0 and 'http' in items[12]['photos'][0]:
    p = download_image(items[12]['photos'][0], "achievements/shaxmat_shashka.jpg")
    if p:
        ach3.photo = p
        ach3.save()

print("[OK] Real achievements saved.")

print("\n--- 5. Creating Real News & Categories ---")
cat_manaviyat, _ = NewsCategory.objects.get_or_create(slug="manaviyat-marifat", defaults={'name': "Ma'naviyat va ma'rifat", 'color': "#4F46E5"})
cat_talim, _ = NewsCategory.objects.get_or_create(slug="talim-va-fan", defaults={'name': "Ta'lim va fan", 'color': "#06B6D4"})
cat_sport, _ = NewsCategory.objects.get_or_create(slug="sport-yangiliklari", defaults={'name': "Sport yangiliklari", 'color': "#10B981"})
cat_tadbirlar, _ = NewsCategory.objects.get_or_create(slug="maktab-tadbirlari", defaults={'name': "Maktab tadbirlari", 'color': "#F59E0B"})

news_articles = [
    {
        'title': "Kelajak soatida O'quvchilar kengashi va sinf vakillari saylovi o'tkazildi",
        'slug': "kelajak-soatida-oquvchilar-kengashi-saylovi",
        'category': cat_manaviyat,
        'excerpt': "Namangan tumanidagi 19-sonli maktabda 'Kelajak soati' darsi doirasida O'quvchilar kengashiga 17 nafar sinf vakili ochiq ovoz berish yo'li bilan saylandi.",
        'content': (
            "Namangan tumanidagi 19-sonli umumiy o'rta ta'lim maktabida “Kelajak soati” darsi doirasida "
            "O'quvchilar kengashi va sinf vakillari saylovi tashkil etildi.\n\n"
            "Maktab maslahatchisi G.Narzullayeva tomonidan o'quvchilarga O'quvchilar kengashining maqsad va vazifalari, "
            "maktab hayotidagi o'rni, shuningdek, yoshlarning faolligi, tashabbuskorligi va yetakchilik qobiliyatini rivojlantirishdagi "
            "ahamiyati haqida tushunchalar berildi.\n\n"
            "Saylov jarayoni ochiq ovoz berish — qo'l ko'tarish orqali o'tkazilib, 5–11-sinflardagi 17 ta sinfdan jami 17 nafar sinf vakili saylandi. "
            "Mazkur saylov o'quvchilarning o'z fikrini erkin ifoda etishi, jamoada faol bo'lishi va maktab hayotida tashabbus bilan ishtirok etishiga xizmat qiladi."
        ),
        'date': datetime(2026, 10, 12, 10, 0),
        'photo_url': items[5]['photos'][0] if len(items[5]['photos']) > 0 and 'http' in items[5]['photos'][0] else None,
        'rel_photo': "news/covers/saylov_kelajak_soati.jpg",
        'is_featured': True,
    },
    {
        'title': "8-A sinfida rus tili fanidan 'Проектная работа' loyiha ishi tashkil etildi",
        'slug': "8-a-sinf-rus-tili-loyiha-ishi",
        'category': cat_talim,
        'excerpt': "Mirxalova Mastura ustozimiz tashabbuslari ostida 8-A sinfida rus tilida nutq o'stirish va jamoaviy fikrlashga qaratilgan amaliy loyiha darsi bo'lib o'tdi.",
        'content': (
            "Namangan tumani 19-sonli maktabning 8-A sinf o'quvchilari o'rtasida rus tili fanidan 'Проектная работа' (Loyiha ishi) tashkil etildi.\n\n"
            "Mazkur loyiha Mirxalova Mastura ustozimizning tashabbuslari ostida ko'tarinki kayfiyatda hamda barcha o'quvchilarning faol ishtirokida o'tkazildi. "
            "Dars davomida o'quvchilar rus tilida o'z loyihalarini taqdimot qildilar. Bu kabi interaktiv loyihalar yoshlarning chet tillarida erkin so'zlashish va nutq o'stirish ko'nikmasini rivojlantirishda katta ahamiyat kasb etadi."
        ),
        'date': datetime(2026, 10, 12, 17, 0),
        'photo_url': items[1]['photos'][0] if len(items[1]['photos']) > 0 and 'http' in items[1]['photos'][0] else None,
        'rel_photo': "news/covers/rus_tili_loyiha.jpg",
        'is_featured': True,
    },
    {
        'title': "Besh tashabbus olimpiadasi: Maktabimiz yengil atletikachilari tuman bosqichida!",
        'slug': "besh-tashabbus-yengil-atletika-goliblik",
        'category': cat_sport,
        'excerpt': "19-maktab yoshlari yengil atletika bo'yicha 4-hudud bosqichida mutlaq g'oliblikni qo'lga kiritib, tuman bosqichiga yo'llanmaga ega bo'lishdi.",
        'content': (
            "Namangan tuman MMTBga qarashli 28-sonli maktabda BESH TASHABBUS olimpiadasining YENGIL ATLETIKA musobaqasi 4-hudud bosqichi o'tkazildi.\n\n"
            "Musobaqada 5 ta maktab jamoalari o'zaro kuch sinashdilar. Qizg'in bahslar natijasida:\n"
            "- 5-6 sinf o'g'il bolalar: 1-o'rin 19-maktab 🥇\n"
            "- 7-8 sinf o'g'il bolalar: 1-o'rin 19-maktab 🥇\n"
            "- 7-8 sinf qiz bolalar: 1-o'rin 19-maktab 🥇\n"
            "- 5-6 sinf qiz bolalar: 2-o'rin 19-maktab 🥈\n\n"
            "Ushbu iqtidorli o'quvchilarimiz tuman miqyosidagi bosqichga yo'llanmani qo'lga kiritishdi. Yosh sportchilarimiz va ularning ustozlariga ulkan zafarlar tilaymiz!"
        ),
        'date': datetime(2026, 10, 10, 9, 0),
        'photo_url': items[4]['photos'][0] if len(items[4]['photos']) > 0 and 'http' in items[4]['photos'][0] else None,
        'rel_photo': "news/covers/yengil_atletika_musobaqa.jpg",
        'is_featured': True,
    },
    {
        'title': "Milliylik — qalbimizdagi qadriyat: 19-maktabda Milliy liboslar tarannumi",
        'slug': "milliylik-qalbimizdagi-qadriyat-19-maktab",
        'category': cat_tadbirlar,
        'excerpt': "Maktabimizda milliy qadriyatlarga hurmat va yosh avlodda faxr tuyg'usini yuksaltirish maqsadida 'Milliy liboslar kuni' keng nishonlandi.",
        'content': (
            "Bugun Namangan tumani 19-maktabda Milliylik tarannumi!\n\n"
            "Milliy libos — ajdodlarimizdan meros bo'lib kelayotgan nafislik, did, madaniyat va o'zlik timsolidir. "
            "Atlas va adrasning betakror jilosi, milliy do'ppi va an'anaviy bezaklar xalqimizning o'ziga xosligini yanada yorqin namoyon etadi.\n\n"
            "Bunday tashabbuslar o'quvchi-yoshlarda milliy qadriyatlarga hurmatni mustahkamlash, madaniy merosimizni asrab-avaylash va yosh avlodga ibrat bo'lishga xizmat qiladi."
        ),
        'date': datetime(2026, 10, 9, 11, 0),
        'photo_url': items[10]['photos'][0] if len(items[10]['photos']) > 0 and 'http' in items[10]['photos'][0] else None,
        'rel_photo': "news/covers/milliylik_tadbir.jpg",
        'is_featured': True,
    },
    {
        'title': "Namangan tumani hokim o'rinbosari Omonjon Saidazimov maktabimizga tashrif buyurdi",
        'slug': "hokim-orinbosari-maktabga-tashrif",
        'category': cat_talim,
        'excerpt': "Tashrif doirasida ta'lim sifati o'rganildi, dars jadvali ko'zdan kechirildi va yuqori sinf o'quvchilariga kasb-hunar bo'yicha tavsiyalar berildi.",
        'content': (
            "Maktabgacha va maktab ta'limi bo'limiga qarashli 19-sonli umumiy o'rta ta'lim maktabiga Namangan tumani ijtimoiy masalalar bo'yicha hokim o'rinbosari Saidazimov Omonjon ta'lim sifatini tekshirish maqsadida tashrif buyurdi.\n\n"
            "Tashrif davomida yuqori sinf o'quvchilariga Oliy ta'lim hamda zamonaviy kasb-hunarlarga oid muhim tavsiyalar berildi. "
            "Dars jadvali, o'tilgan mavzular va o'quvchilarning bilim saviyasi yuzasidan samimiy savol-javoblar o'tkazildi."
        ),
        'date': datetime(2026, 10, 7, 14, 0),
        'photo_url': items[7]['photos'][0] if len(items[7]['photos']) > 0 and 'http' in items[7]['photos'][0] else None,
        'rel_photo': "news/covers/hokim_urinbosari_tashrif.jpg",
        'is_featured': False,
    },
    {
        'title': "1-oktabr — Ustoz va murabbiylar kuni: Faxriy pedagoglar xonadonlariga tashrif",
        'slug': "ustoz-va-murabbiylar-kuni-faxriy-ustozlar",
        'category': cat_manaviyat,
        'excerpt': "O'quvchilarimiz ko'p yillar maktabda sidqidildan mehnat qilgan faxriy va nafaqadagi ustozlarning holidan xabar oldilar.",
        'content': (
            "1-oktabr — Ustoz va murabbiylar kuni munosabati bilan 19-maktab o'quvchilari uzoq yillar ta'lim-tarbiya bergan faxriy ustozlar xonadonlariga tashrif buyurdilar.\n\n"
            "Jumladan, 11-B sinf o'quvchilari faxriy ingliz tili o'qituvchisi Ubaydullayev Hamidullo domlani, 7-B sinf o'quvchilari Yunusova Gulbahor ustozni, 6-A sinf o'quvchilari Xalilova Azizaxon oyani, shuningdek Azizov domla va M. Mo'minov domlalarni samimiy tabrikladilar.\n\n"
            "Kattalarni qadrlash, ustozlarga ehtirom ko'rsatish — maktabimizning ezgu an'analaridan biridir."
        ),
        'date': datetime(2026, 10, 1, 10, 0),
        'photo_url': items[18]['photos'][0] if len(items[18]['photos']) > 0 and 'http' in items[18]['photos'][0] else None,
        'rel_photo': "news/covers/faxriy_ustozlar_tabrik.jpg",
        'is_featured': False,
    },
]

for na in news_articles:
    n_obj, _ = News.objects.get_or_create(slug=na['slug'])
    n_obj.title = na['title']
    n_obj.category = na['category']
    n_obj.excerpt = na['excerpt']
    n_obj.content = na['content']
    n_obj.status = 'published'
    n_obj.is_featured = na['is_featured']
    n_obj.published_at = na['date']
    n_obj.views_count = 142
    
    if na['photo_url']:
        p = download_image(na['photo_url'], na['rel_photo'])
        if p:
            n_obj.cover_image = p
    n_obj.save()
    print(f"[OK] News saved: {n_obj.title}")

print("\n--- 6. Creating Gallery Images ---")
gallery_items = [
    ("Kelajak soatida saylov jarayonlari", items[0]['photos'][0] if len(items[0]['photos']) > 0 and 'http' in items[0]['photos'][0] else None, "events"),
    ("Rus tili darsidagi loyiha ishlari", items[1]['photos'][1] if len(items[1]['photos']) > 1 and 'http' in items[1]['photos'][1] else None, "school"),
    ("Besh tashabbus Yengil atletika qizg'in bahslar", items[4]['photos'][1] if len(items[4]['photos']) > 1 and 'http' in items[4]['photos'][1] else None, "sports"),
    ("Milliylik — Milliy liboslar kunidan lavhalar", items[10]['photos'][0] if len(items[10]['photos']) > 0 and 'http' in items[10]['photos'][0] else None, "events"),
    ("Shaxmat-shashka musobaqalari", items[12]['photos'][1] if len(items[12]['photos']) > 1 and 'http' in items[12]['photos'][1] else None, "sports"),
    ("Ustozlar kuni xonadonlarga tashrif", items[18]['photos'][1] if len(items[18]['photos']) > 1 and 'http' in items[18]['photos'][1] else None, "events"),
]

for idx, (title, p_url, cat) in enumerate(gallery_items):
    if p_url:
        rel_p = f"gallery/gallery_{idx+1}.jpg"
        p = download_image(p_url, rel_p)
        if p:
            GalleryImage.objects.get_or_create(
                title=title,
                defaults={
                    'category': cat,
                    'image': p,
                    'is_active': True,
                    'order': idx + 1
                }
            )
            print(f"[OK] Gallery image saved: {title}")

print("\n==========================================")
print("ALL REAL DATA IMPORTED SUCCESSFULLY!")
print("==========================================")
