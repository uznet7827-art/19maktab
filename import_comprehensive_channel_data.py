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
    if not url or 'http' not in url or 'emoji' in url:
        return None
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
            print(f"[Download Error] {rel_path}: {e}")
            return None
    return rel_path

print("=== 1. UPDATING SITE SETTINGS ===")
site = SiteSettings.objects.first()
if not site:
    site = SiteSettings.objects.create(school_name="19-sonli umumiy o'rta ta'lim maktabi")

site.school_name = "19-sonli umumiy o'rta ta'lim maktabi"
site.school_name_ru = "Общеобразовательная школа №19"
site.school_name_en = "Secondary School #19"
site.tagline = "Sifatli ta'lim, yetakchi yoshlar va yorqin kelajak poydevori!"
site.director_name = "M. Nabiyeva"
site.director_message = (
    "Bizning 19-umumiy o'rta ta'lim maktabimiz har bir o'quvchining qobiliyati va iqtidorini ro'yobga chiqarish, "
    "yoshlarni qonunlarga hurmat, yuksak ma'naviyat va zamonaviy ilm-fan ruhida tarbiyalashni bosh maqsad qilib qo'ygan. "
    "Maktabimiz eshiklari barcha yoshlarimiz uchun yuksak marralar va orzular sari hamisha ochiqdir!"
)
site.address = "Namangan viloyati, Namangan tumani, 19-sonli umumiy o'rta ta'lim maktabi"
site.telegram_url = "https://t.me/qwert19idum"
site.save()
print(f"[OK] Director: {site.director_name} | School: {site.school_name}")

print("\n=== 2. CREATING / UPDATING DEPARTMENTS ===")
dept_lang, _ = Department.objects.get_or_create(name="Tillar kafedrasi", defaults={'name_ru': "Кафедра языков", 'name_en': "Department of Languages"})
dept_exact, _ = Department.objects.get_or_create(name="Aniq va tabiiy fanlar", defaults={'name_ru': "Точные науки", 'name_en': "Exact & Natural Sciences"})
dept_manaviy, _ = Department.objects.get_or_create(name="Ma'naviy-ma'rifiy va sport", defaults={'name_ru': "Духовно-просветительское и спорт", 'name_en': "Spiritual, Educational & Sports"})
dept_primary, _ = Department.objects.get_or_create(name="Boshlang'ich ta'lim", defaults={'name_ru': "Начальное образование", 'name_en': "Primary Education"})
dept_inklyuziv, _ = Department.objects.get_or_create(name="Inklyuziv va maxsus pedagogika", defaults={'name_ru': "Инклюзивное образование", 'name_en': "Inclusive & Special Education"})
dept_faxriy, _ = Department.objects.get_or_create(name="Faxriy ustozlar", defaults={'name_ru': "Почетные учителя", 'name_en': "Honorary Senior Teachers"})

json_path = os.path.join(BASE_DIR, 'all_deep_channel_posts.json')
posts = json.load(open(json_path, encoding='utf-8')) if os.path.exists(json_path) else []

print("\n=== 3. CREATING / UPDATING ALL TEACHERS ===")
Teacher.objects.filter(full_name__in=[
    "Odina", "Abdullayev Rustam Shokirovich", "Sobirova Dilnoza Erkinovna", 
    "Usmonov Jasur Alisherovich", "Bekmirzayeva N.", "Narzullayeva G."
]).delete()
all_teachers = [
    {
        'full_name': "M. Nabiyeva",
        'subject': "Maktab direktori",
        'position': "19-sonli maktab direktori",
        'department': dept_manaviy,
        'bio': "19-umumiy o'rta ta'lim maktabi rahbari. Maktabda ta'lim sifatini oshirish, o'quvchilar intizomi va 'Ustozga ehtirom' ijodiy tanlovlari tashabbuskori.",
        'experience_years': 22,
        'order': 1,
        'rel_photo': "director/director.png",
        'photo_url': None, # Already have director.png!
    },
    {
        'full_name': "Shokirova M.",
        'subject': "MMIBDO'",
        'position': "Ma'naviy-ma'rifiy ishlar bo'yicha direktor o'rinbosari",
        'department': dept_manaviy,
        'bio': "Maktabning tarbiyaviy, ma'naviy-ma'rifiy jarayonlari, o'quvchilar kengashi va yoshlar tashabbuslarini muvofiqlashtiruvchi rahbar.",
        'experience_years': 16,
        'order': 2,
        'rel_photo': "teachers/m_shokirova.jpg",
        'photo_url': posts[3]['photos'][0] if len(posts[3]['photos']) > 0 else None,
    },
    {
        'full_name': "Mirxalova Mastura",
        'subject': "Rus tili va adabiyoti",
        'position': "Yetakchi o'qituvchi, 8-A va 11-A sinf rahbari",
        'department': dept_lang,
        'bio': "8-A va 11-A sinflari rahbari. Rus tili fanidan interaktiv metodlar va 'Проектная работа' loyihalari asoschisi.",
        'experience_years': 18,
        'order': 3,
        'rel_photo': "teachers/mastura_mirxalova.jpg",
        'photo_url': posts[1]['photos'][0] if len(posts[1]['photos']) > 0 else None,
    },
    {
        'full_name': "Narzullayeva Gulnoza",
        'subject': "Maktab maslahatchisi",
        'position': "Maktab maslahatchisi, Yoshlar yetakchisi",
        'department': dept_manaviy,
        'bio': "Maktabda 'Kelajak soati', O'quvchilar kengashi saylovlari va ijodkor o'quvchilar tashabbuslarini qo'llab-quvvatlovchi yetakchi mutaxassis.",
        'experience_years': 12,
        'order': 4,
        'rel_photo': "teachers/g_narzullayeva.jpg",
        'photo_url': posts[3]['photos'][0] if len(posts) > 3 and len(posts[3]['photos']) > 0 else None,
    },
    {
        'full_name': "Bekmirzayeva Nafisa",
        'subject': "Maktab psixologi",
        'position': "Amaliyotchi psixolog",
        'department': dept_manaviy,
        'bio': "O'quvchilar bilan 'O'ziga ishonch' treninglari, kasbga yo'naltirish va alohida ehtiyojli bolalar bilan psixologik mashg'ulotlar o'tkazuvchi mutaxassis.",
        'experience_years': 11,
        'order': 5,
        'rel_photo': "teachers/n_bekmirzayeva.jpg",
        'photo_url': posts[3]['photos'][1] if len(posts[3]['photos']) > 1 else None,
    },
    {
        'full_name': "Xabibullayeva Sarvinoz",
        'subject': "Maxsus pedagogika",
        'position': "Maxsus pedagog, Inkluziv ta'lim ustozi",
        'department': dept_inklyuziv,
        'bio': "Alohida ta'lim ehtiyojlari bo'lgan o'quvchilar bilan ijodiy mashg'ulotlar, rasm va qo'l mehnati to'garaklari rahbari.",
        'experience_years': 9,
        'order': 6,
        'rel_photo': "teachers/s_xabibullayeva.jpg",
        'photo_url': posts[92]['photos'][0] if len(posts[92]['photos']) > 0 else None,
    },
    {
        'full_name': "Vahobova Sharifaxon",
        'subject': "Ona tili va adabiyot",
        'position': "Oliy toifali ona tili va adabiyot o'qituvchisi",
        'department': dept_lang,
        'bio': "Maktabimizning jonkuyar adabiyot ustozi. Yosh shoir va yozuvchilar, ijodkor o'quvchilar murabbiyi.",
        'experience_years': 20,
        'order': 7,
        'rel_photo': "teachers/sharifaxon_vahobova.jpg",
        'photo_url': posts[35]['photos'][0] if len(posts[35]['photos']) > 0 else None,
    },
    {
        'full_name': "Xamdamova S.",
        'subject': "Jismoniy tarbiya",
        'position': "Jismoniy tarbiya o'qituvchisi, Besh tashabbus bosh hakami",
        'department': dept_manaviy,
        'bio': "Maktab shaxmat-shashka va sport to'garaklari rahbari. 'Besh tashabbus' olimpiadasi hududiy musobaqalari bosh hakami.",
        'experience_years': 15,
        'order': 8,
        'rel_photo': "teachers/s_xamdamova.jpg",
        'photo_url': posts[13]['photos'][0] if len(posts[13]['photos']) > 0 else None,
    },
    {
        'full_name': "Xasanova M.",
        'subject': "Tarbiyaviy ishlar",
        'position': "Xotin-qizlar masalalari bo'yicha mas'ul pedagog",
        'department': dept_manaviy,
        'bio': "Qizlar tarbiyasi, odob-axloq, kiyinish madaniyati va milliy qadriyatlarni targ'ib qiluvchi tajribali pedagog.",
        'experience_years': 17,
        'order': 9,
        'rel_photo': "teachers/m_xasanova.jpg",
        'photo_url': posts[3]['photos'][2] if len(posts[3]['photos']) > 2 else None,
    },
    {
        'full_name': "Ubaydullayeva M.",
        'subject': "Aniq fanlar, 11-B sinf rahbari",
        'position': "11-B sinf rahbari, Yetakchi ustoz",
        'department': dept_exact,
        'bio': "Bitiruvchi sinf o'quvchilarining oliy ta'limga kirishi va kasb tanlashiga yo'naltiruvchi jonkuyar murabbiy.",
        'experience_years': 19,
        'order': 10,
        'rel_photo': "teachers/m_ubaydullayeva.jpg",
        'photo_url': posts[8]['photos'][0] if len(posts[8]['photos']) > 0 else None,
    },
    # Faxriy ustozlar
    {
        'full_name': "Ubaydullayev Hamidullo",
        'subject': "Ingliz tili (Faxriy)",
        'position': "Nafaqadagi faxriy ingliz tili ustozi",
        'department': dept_faxriy,
        'bio': "Maktabimizda ko'p yillar ingliz tili fanidan yuzlab iqtidorli shogirdlarni kamolga yetkazgan faxriy ustoz.",
        'experience_years': 42,
        'order': 11,
        'rel_photo': "teachers/hamidullo_ubaydullayev.jpg",
        'photo_url': posts[18]['photos'][0] if len(posts[18]['photos']) > 0 else None,
    },
    {
        'full_name': "Otaboyev Ildor",
        'subject': "Adabiyot va ma'naviyat (Faxriy)",
        'position': "Faxriy ustoz, adabiyot fani",
        'department': dept_faxriy,
        'bio': "Maktabimizning faxriy ustozlaridan biri. 'Ustozga ehtirom' tadbirlari faxriy mehmoni.",
        'experience_years': 40,
        'order': 12,
        'rel_photo': "teachers/ildor_otaboyev.jpg",
        'photo_url': posts[47]['photos'][2] if len(posts) > 47 and len(posts[47]['photos']) > 2 else None,
    },
    {
        'full_name': "Yunusova Gulbahor",
        'subject': "Boshlang'ich ta'lim (Faxriy)",
        'position': "Nafaqadagi faxriy ustoz",
        'department': dept_faxriy,
        'bio': "Xalq ta'limi a'lochisi, boshlang'ich sinf faxriy o'qituvchisi.",
        'experience_years': 38,
        'order': 13,
        'rel_photo': "teachers/gulbahor_yunusova.jpg",
        'photo_url': posts[16]['photos'][0] if len(posts[16]['photos']) > 0 else None,
    },
    {
        'full_name': "Xalilova Azizaxon",
        'subject': "Faxriy pedagog",
        'position': "Nafaqadagi faxriy ustoz",
        'department': dept_faxriy,
        'bio': "Uzoq yillar 19-maktabda yosh avlodga ta'lim-tarbiya bergan faxriy ustoz.",
        'experience_years': 36,
        'order': 14,
        'rel_photo': "teachers/azizaxon_xalilova.jpg",
        'photo_url': posts[26]['photos'][0] if len(posts[26]['photos']) > 0 else None,
    },
    {
        'full_name': "Azizov domla",
        'subject': "Faxriy ustoz",
        'position': "Maktabimiz faxriy ustozi",
        'department': dept_faxriy,
        'bio': "19-maktabning ko'p yillik fidoyi faxriy o'qituvchisi.",
        'experience_years': 39,
        'order': 15,
        'rel_photo': "teachers/azizov_domla.jpg",
        'photo_url': posts[27]['photos'][0] if len(posts[27]['photos']) > 0 else None,
    },
    {
        'full_name': "Mo'minov M. domla",
        'subject': "Faxriy ustoz",
        'position': "Maktabimiz faxriy ustozi",
        'department': dept_faxriy,
        'bio': "Fidoyi pedagog, ko'plab avlod vakillarining sevimli ustozi.",
        'experience_years': 41,
        'order': 16,
        'rel_photo': "teachers/mominov_domla.jpg",
        'photo_url': posts[28]['photos'][0] if len(posts[28]['photos']) > 0 else None,
    },
]

for td in all_teachers:
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
        p = download_image(td['photo_url'], td['rel_photo'])
        if p:
            t_obj.photo = p
    elif td['rel_photo'] and os.path.exists(os.path.join(BASE_DIR, 'media', td['rel_photo'])):
        t_obj.photo = td['rel_photo']
    t_obj.save()
    print(f"[OK] Teacher saved: {t_obj.full_name} ({t_obj.position})")

print("\n=== 4. CREATING ALL REAL ACHIEVEMENTS ===")
achievements_list = [
    {
        'student_name': "Akramaliyeva Shodiya",
        'grade': "10-sinf",
        'type': 'art',
        'title': "'Elning erka qiziman' kitobi muallifi va Ijodkor bolalar tanlovi 3-o'rin sohibasi",
        'desc': (
            "10-sinf o'quvchisi Akramaliyeva Shodiyaning 'Elning erka qiziman' nomli birinchi she'riy to'plami nashrdan chiqdi. "
            "U Kitobxonlik festivali doirasida 'Ijodkor bolalar' ko'rik-tanlovining Namangan viloyati bosqichida 3-o'rinni egalladi "
            "hamda Namangan televideniyesining 'Guldasta' dasturida jonli efirda chiqish qildi."
        ),
        'date': date(2026, 9, 25),
        'place': "3-o'rin (Viloyat)",
        'photo_url': posts[35]['photos'][0] if len(posts[35]['photos']) > 0 else None,
        'rel_photo': "achievements/shodiya_akramaliyeva.jpg"
    },
    {
        'student_name': "Abdusattorova Nigora",
        'grade': "6-A sinf",
        'type': 'olympiad',
        'title': "Kelajak yulduzlari viloyat ochiq olimpiadasi — Super Oliy o'rin!",
        'desc': (
            "Farg'ona viloyatida o'tkazilgan 'Kelajak yulduzlari ochiq olimpiadasi'da ingliz tili fanidan ishtirok etib, "
            "faxrli 'Super oliy' o'rinni egalladi va maxsus sertifikat bilan taqdirlandi."
        ),
        'date': date(2026, 10, 1),
        'place': "Super Oliy",
        'photo_url': posts[21]['photos'][0] if len(posts[21]['photos']) > 0 else None,
        'rel_photo': "achievements/nigora_abdusattorova.jpg"
    },
    {
        'student_name': "Solibayev Inonjon",
        'grade': "1-A sinf",
        'type': 'science',
        'title': "ZIYO SAMM ACADEMY Respublika turnirida Mental arifmetika bo'yicha Oliy o'rin!",
        'desc': (
            "Andijon shahrida 'ZIYO SAMM ACADEMY' tashkiloti tomonidan o'tkazilgan respublika ochiq turnirida "
            "Mental arifmetikadan faxrli Oliy o'rinni egalladi va qimmatbaho sovg'alar bilan taqdirlandi."
        ),
        'date': date(2026, 9, 21),
        'place': "Oliy o'rin",
        'photo_url': posts[57]['photos'][0] if len(posts[57]['photos']) > 0 else None,
        'rel_photo': "achievements/inonjon_solibayev.jpg"
    },
    {
        'student_name': "19-maktab Yengil atletika jamoasi (O'g'il bolalar 5-6 sinf)",
        'grade': "5-6 sinf",
        'type': 'sport',
        'title': "Besh tashabbus Yengil atletika musobaqasi — 1-o'rin va tuman yo'llanmasi",
        'desc': "4-hudud bosqichida 5 ta maktab jamoalari o'rtasida 1-o'rinni qo'lga kiritdi.",
        'date': date(2026, 10, 10),
        'place': "1-o'rin",
        'photo_url': posts[4]['photos'][0] if len(posts[4]['photos']) > 0 else None,
        'rel_photo': "achievements/yengil_atletika_5_6_ogil.jpg"
    },
    {
        'student_name': "19-maktab Yengil atletika jamoasi (7-8 sinf o'g'il va qizlar)",
        'grade': "7-8 sinf",
        'type': 'sport',
        'title': "Besh tashabbus Yengil atletika 7-8 sinflar — 1-o'rin",
        'desc': "7-8 sinflar o'g'il bolalar va qizlar jamoamiz tengsiz deb topilib, 1-o'rinni egalladi.",
        'date': date(2026, 10, 10),
        'place': "1-o'rin",
        'photo_url': posts[4]['photos'][1] if len(posts[4]['photos']) > 1 else None,
        'rel_photo': "achievements/yengil_atletika_7_8.jpg"
    },
    {
        'student_name': "19-maktab Shaxmat-shashka qizlar jamoasi",
        'grade': "5-11 sinf",
        'type': 'sport',
        'title': "Besh tashabbus Shaxmat-shashka 5-11 sinf qizlar — 1-o'rin",
        'desc': "Shaxmat-shashka 4-hudud musobaqalarida maktabimizning 5-11 sinf qizlar jamoasi 1-o'rinni qo'lga kiritdi.",
        'date': date(2026, 10, 10),
        'place': "1-o'rin",
        'photo_url': posts[12]['photos'][0] if len(posts[12]['photos']) > 0 else None,
        'rel_photo': "achievements/shaxmat_shashka_qizlar.jpg"
    },
]

for ach in achievements_list:
    ach_obj, _ = Achievement.objects.get_or_create(
        student_name=ach['student_name'],
        title=ach['title'],
        defaults={
            'grade': ach['grade'],
            'achievement_type': ach['type'],
            'description': ach['desc'],
            'date': ach['date'],
            'place': ach['place'],
            'is_active': True,
            'parent_consent': True,
        }
    )
    if ach['photo_url']:
        p = download_image(ach['photo_url'], ach['rel_photo'])
        if p:
            ach_obj.photo = p
            ach_obj.save()
    print(f"[OK] Achievement saved: {ach_obj.student_name} - {ach_obj.title}")

print("\n=== 5. CREATING ALL REAL NEWS ===")
cat_manaviyat, _ = NewsCategory.objects.get_or_create(slug="manaviyat-marifat", defaults={'name': "Ma'naviyat va ma'rifat", 'color': "#4F46E5"})
cat_talim, _ = NewsCategory.objects.get_or_create(slug="talim-va-fan", defaults={'name': "Ta'lim va fan", 'color': "#06B6D4"})
cat_sport, _ = NewsCategory.objects.get_or_create(slug="sport-yangiliklari", defaults={'name': "Sport yangiliklari", 'color': "#10B981"})
cat_tadbirlar, _ = NewsCategory.objects.get_or_create(slug="maktab-tadbirlari", defaults={'name': "Maktab tadbirlari", 'color': "#F59E0B"})

news_list = [
    {
        'title': "10-sinf o'quvchisi Akramaliyeva Shodiyaning 'Elning erka qiziman' kitobi taqdimoti o'tkazildi",
        'slug': "shodiya-akramaliyeva-kitob-taqdimoti",
        'category': cat_manaviyat,
        'excerpt': "O'zbekiston Yozuvchilar uyushmasi vakillari va faxriy ustozlar ishtirokida maktabimizning iqtidorli shoira qizi kitobining tantanali taqdimoti bo'lib o'tdi.",
        'content': (
            "Namangan tumani 19-umumiy o'rta ta'lim maktabida 10-sinf o'quvchisi Akramaliyeva Shodiyaning 'Elning erka qiziman' nomli kitobi taqdimoti o'tkazildi.\n\n"
            "Mazkur nufuzli adabiy tadbirga O'zbekiston Respublikasi Yozuvchilar uyushmasi a'zosi, jurnalist Alisher Jo'rayev, "
            "faxriy ustoz Otaboyev Ildor, maktab direktori M. Nabiyeva, ona tili fani ustozi Vahobova Sharifaxon hamda maktab maslahatchisi G. Narzullayeva tashrif buyurdilar.\n\n"
            "Tadbir davomida Shodiyaning she'rlaridan namunalar o'qildi, sahna ko'rinishlari va kuy-qo'shiqlar ijro etildi. "
            "Shuningdek, maktab direktori M. Nabiyeva tashabbusi bilan 'Ustozga ehtirom' ijodiy ishlar tanlovi g'oliblari tantanali taqdirlandi."
        ),
        'date': datetime(2026, 9, 25, 14, 0),
        'photo_url': posts[35]['photos'][0] if len(posts[35]['photos']) > 0 else None,
        'rel_photo': "news/covers/shodiya_kitob_taqdimoti.jpg",
        'is_featured': True,
    },
    {
        'title': "Kelajak soatida O'quvchilar kengashi va sinf vakillari saylovi o'tkazildi",
        'slug': "kelajak-soatida-oquvchilar-kengashi-saylovi",
        'category': cat_manaviyat,
        'excerpt': "19-maktabda 'Kelajak soati' darsi doirasida 5-11 sinflardan jami 17 nafar faol sinf vakillari O'quvchilar kengashiga saylandi.",
        'content': (
            "Namangan tumanidagi 19-sonli umumiy o'rta ta'lim maktabida “Kelajak soati” darsi doirasida "
            "O'quvchilar kengashi va sinf vakillari saylovi tashkil etildi.\n\n"
            "Maktab maslahatchisi G. Narzullayeva tomonidan o'quvchilarga O'quvchilar kengashining maqsad va vazifalari, "
            "maktab hayotidagi o'rni, shuningdek, yoshlarning yetakchilik qobiliyatini rivojlantirishdagi ahamiyati haqida tushunchalar berildi.\n\n"
            "Saylov jarayoni ochiq ovoz berish orqali o'tkazilib, 5–11-sinflardan jami 17 nafar eng munosib sinf vakillari saylandi."
        ),
        'date': datetime(2026, 10, 12, 10, 0),
        'photo_url': posts[0]['photos'][0] if len(posts[0]['photos']) > 0 else None,
        'rel_photo': "news/covers/saylov_kelajak_soati.jpg",
        'is_featured': True,
    },
    {
        'title': "8-A sinfida rus tili fanidan 'Проектная работа' loyiha darsi tashkil etildi",
        'slug': "8-a-sinf-rus-tili-loyiha-ishi",
        'category': cat_talim,
        'excerpt': "Mirxalova Mastura ustozimiz tashabbusi bilan 8-A sinfida chet tilida nutq o'stirishga qaratilgan amaliy loyiha darsi o'tkazildi.",
        'content': (
            "Namangan tumani 19-sonli maktabning 8-A sinf o'quvchilari o'rtasida rus tili fanidan 'Проектная работа' (Loyiha ishi) tashkil etildi.\n\n"
            "Mazkur loyiha Mirxalova Mastura ustozimizning tashabbuslari ostida ko'tarinki kayfiyatda hamda barcha o'quvchilarning faol ishtirokida o'tkazildi. "
            "O'quvchilar o'z loyihalarini taqdimot qilib, erkin muloqot va nutq o'stirish mahoratlarini namoyish etdilar."
        ),
        'date': datetime(2026, 10, 12, 17, 0),
        'photo_url': posts[1]['photos'][0] if len(posts[1]['photos']) > 0 else None,
        'rel_photo': "news/covers/rus_tili_loyiha.jpg",
        'is_featured': True,
    },
    {
        'title': "Besh tashabbus olimpiadasi: Yengil atletika bo'yicha maktabimiz g'olib!",
        'slug': "besh-tashabbus-yengil-atletika-goliblik",
        'category': cat_sport,
        'excerpt': "19-maktab yoshlari yengil atletika bo'yicha 4-hudud bosqichida mutlaq g'oliblikni qo'lga kiritib, tuman bosqichiga yo'llanmaga ega bo'lishdi.",
        'content': (
            "Besh tashabbus olimpiadasining Yengil atletika musobaqasi 4-hudud bosqichida 19-maktab jamoasi ajoyib natijalar qayd etdi:\n"
            "- 5-6 sinf o'g'il bolalar: 1-o'rin 19-maktab 🥇\n"
            "- 7-8 sinf o'g'il bolalar: 1-o'rin 19-maktab 🥇\n"
            "- 7-8 sinf qiz bolalar: 1-o'rin 19-maktab 🥇\n"
            "- 5-6 sinf qiz bolalar: 2-o'rin 19-maktab 🥈\n\n"
            "Ushbu iqtidorli o'quvchilarimiz tuman bosqichiga yo'llanmani qo'lga kiritishdi!"
        ),
        'date': datetime(2026, 10, 10, 9, 0),
        'photo_url': posts[4]['photos'][0] if len(posts[4]['photos']) > 0 else None,
        'rel_photo': "news/covers/yengil_atletika_musobaqa.jpg",
        'is_featured': True,
    },
    {
        'title': "Milliylik — qalbimizdagi qadriyat: 19-maktabda Milliy liboslar tarannumi",
        'slug': "milliylik-qalbimizdagi-qadriyat-19-maktab",
        'category': cat_tadbirlar,
        'excerpt': "Maktabimizda milliy qadriyatlarga hurmat va o'zlikni anglash tuyg'ularini yuksaltirish maqsadida 'Milliy liboslar kuni' keng nishonlandi.",
        'content': (
            "Namangan tumani 19-maktabda Milliylik tarannumi!\n\n"
            "Milliy libos — ajdodlarimizdan meros bo'lib kelayotgan nafislik, did, madaniyat va o'zlik timsolidir. "
            "Atlas va adrasning betakror jilosi, milliy do'ppi va an'anaviy bezaklar xalqimizning o'ziga xosligini yanada yorqin namoyon etdi."
        ),
        'date': datetime(2026, 10, 9, 11, 0),
        'photo_url': posts[6]['photos'][0] if len(posts) > 6 and len(posts[6]['photos']) > 0 else None,
        'rel_photo': "news/covers/milliylik_tadbir.jpg",
        'is_featured': True,
    },
    {
        'title': "Maktabimizda 'Jadidlar izidan' ko'rik-tanlovining maktab bosqichi bo'lib o'tdi",
        'slug': "jadidlar-izidan-tanlovi-maktab-bosqichi",
        'category': cat_talim,
        'excerpt': "Ona tili va adabiyot kafedrasi hamda maktab maslahatchisi hamkorligida buyuk ma'rifatparvar ajdodlarimiz xotirasiga bag'ishlangan ko'rik-tanlov tashkil etildi.",
        'content': (
            "Maktabimiz o'quvchilari o'rtasida 'Jadidlar izidan' tanlovining maktab bosqichi o'tkazildi.\n\n"
            "Tanlov o'quvchilar o'rtasida kitobxonlikni keng targ'ib qilish bilan bir qatorda ma'rifatparvar jadid bobolarimiz merosini chuqur o'rganishga zamin yaratdi. "
            "Ona tili o'qituvchilari tomonidan o'quvchilarga kerakli adabiyotlar va tarixiy ma'lumotlar taqdim etildi."
        ),
        'date': datetime(2026, 9, 22, 10, 0),
        'photo_url': posts[47]['photos'][3] if len(posts) > 47 and len(posts[47]['photos']) > 3 else None,
        'rel_photo': "news/covers/jadidlar_izidan.jpg",
        'is_featured': False,
    },
    {
        'title': "Huquqbuzarliklar profilaktikasi va davomat: Profilaktika inspektorlari bilan kengaytirilgan uchrashuv",
        'slug': "huquqbuzarliklar-profilaktikasi-davomat-yigilish",
        'category': cat_manaviyat,
        'excerpt': "Maktab direktori M. Nabiyeva, psixolog N. Bekmirzayeva va mahalla profilaktika inspektorlari ishtirokida 7-11 sinf o'quvchilari bilan uchrashuv o'tkazildi.",
        'content': (
            "19-sonli maktabda 7-11 sinf o'quvchilari o'rtasida jinoyatchilik va huquqbuzarliklarning oldini olishga bag'ishlangan uchrashuv tashkil etildi.\n\n"
            "Yig'ilishda maktab direktori M. Nabiyeva, Dehqonobod MFY profilaktika inspektori M. Tursunov, Mullakuding MFY inspektori A. Malikov hamda psixolog N. Bekmirzayeva ishtirok etdilar. "
            "Yoshlarning bo'sh vaqtlarini mazmunli tashkil etish, darslarga to'liq qatnashish va odob-axloq qoidalariga rioya qilish bo'yicha tushuntirishlar berildi."
        ),
        'date': datetime(2026, 9, 22, 10, 30),
        'photo_url': posts[37]['photos'][0] if len(posts[37]['photos']) > 0 else None,
        'rel_photo': "news/covers/profilaktika_yigilishi.jpg",
        'is_featured': False,
    },
    {
        'title': "Mustaqilligimizning 35 yilligi: 'Mustaqillik — mening nigohimda' ijodiy ko'rgazmasi",
        'slug': "mustaqillik-mening-nigohimda-korgazma",
        'category': cat_tadbirlar,
        'excerpt': "Maktab psixologi N. Bekmirzayeva va maxsus pedagog S. Xabibullayeva rahbarligida alohida ta'lim ehtiyojlari bo'lgan o'quvchilarimiz ijodiy ko'rgazmasi namoyish etildi.",
        'content': (
            "19-sonli maktabda O'zbekiston Respublikasi Mustaqilligining 35 yilligi munosabati bilan "
            "alohida ta'lim ehtiyojlari bo'lgan o'quvchilarimizning 'Mustaqillik — mening nigohimda' mavzusidagi ijodiy rasmlari ko'rgazmasi o'tkazildi.\n\n"
            "Chizilgan har bir rasmda o'quvchilarimizning Vatanga bo'lgan cheksiz mehri, tinch va osuda hayot haqidagi tasavvurlari aks etdi. "
            "Maktab psixologi Bekmirzayeva Nafisa va maxsus pedagog Xabibullayeva Sarvinoz o'quvchilarning qobiliyatini yuzaga chiqarishda faol ko'maklashdilar."
        ),
        'date': datetime(2026, 9, 4, 11, 0),
        'photo_url': posts[92]['photos'][0] if len(posts[92]['photos']) > 0 else None,
        'rel_photo': "news/covers/mustaqillik_korgazma.jpg",
        'is_featured': False,
    },
    {
        'title': "1-oktabr — Ustoz va murabbiylar kuni: Faxriy pedagoglar xonadonlariga tashrif",
        'slug': "ustoz-va-murabbiylar-kuni-faxriy-ustozlar",
        'category': cat_manaviyat,
        'excerpt': "Maktabimiz o'quvchilari uzoq yillar ta'lim bergan faxriy ustozlar holidan xabar olib, ularga chuqur ehtirom bildirdilar.",
        'content': (
            "Ustoz va murabbiylar kuni munosabati bilan 19-maktab o'quvchilari faxriy pedagoglar xonadonlariga tashrif buyurdilar.\n\n"
            "O'quvchilarimiz faxriy ingliz tili ustozi Ubaydullayev Hamidullo, Yunusova Gulbahor, Xalilova Azizaxon, Azizov domla va M. Mo'minov domlalarni bayram bilan samimiy muborakbod etdilar."
        ),
        'date': datetime(2026, 10, 1, 10, 0),
        'photo_url': posts[18]['photos'][0] if len(posts[18]['photos']) > 0 else None,
        'rel_photo': "news/covers/faxriy_ustozlar_tabrik.jpg",
        'is_featured': False,
    },
    {
        'title': "Namangan tumani hokim o'rinbosari Omonjon Saidazimov maktabimizga tashrif buyurdi",
        'slug': "hokim-orinbosari-maktabga-tashrif",
        'category': cat_talim,
        'excerpt': "Tashrif davomida ta'lim sifati o'rganildi va yuqori sinf o'quvchilariga oliy ta'lim hamda kasb-hunarga oid tavsiyalar berildi.",
        'content': (
            "Namangan tumani ijtimoiy masalalar bo'yicha hokim o'rinbosari Saidazimov Omonjon maktabimizga tashrif buyurdi.\n\n"
            "Uchrashuv davomida dars jarayonlari, dars jadvali va o'quvchilarning bilim saviyasi o'rganilib, "
            "bitiruvchi yoshlar bilan kelajak kasblari va oliy ta'limga kirish masalalarida suhbat o'tkazildi."
        ),
        'date': datetime(2026, 10, 7, 14, 0),
        'photo_url': posts[7]['photos'][0] if len(posts[7]['photos']) > 0 else None,
        'rel_photo': "news/covers/hokim_urinbosari_tashrif.jpg",
        'is_featured': False,
    },
    {
        'title': "19-maktabda o'quvchi qizlar bilan kengaytirilgan ma'naviy-tarbiyaviy yig'ilish o'tkazildi",
        'slug': "qizlar-yigilishi-odob-axloq-va-tartib-intizom",
        'category': cat_manaviyat,
        'excerpt': "8-11 sinflardan 100 nafar o'quvchi qizlar hamda pedagoglar ishtirokida odob-axloq, kiyinish madaniyati va intizom bo'yicha yig'ilish bo'lib o'tdi.",
        'content': (
            "13.10.2026 kuni Namangan tumani maktabgacha va maktab ta'limi bo'limiga qarashli 19-sonli umumiy o'rta ta'lim maktabida navbatdagi qizlar yig'ilishi o'tkazildi.\n\n"
            "Yig'ilishda 8-9-10-11 sinflardan 100 nafar o'quvchi qizlar, 10 nafar o'qituvchi hamda sinf rahbarlari ishtirok etishdi.\n\n"
            "Yig'ilishda MMIBDO' M. Shokirova, Xotin-qizlar masalalari bo'yicha mas'ul pedagog M. Xasanova, maktab amaliyotchi psixologi N. Bekmirzayeva hamda maktab maslahatchisi G. Narzullayeva ishtirok etdilar.\n\n"
            "Yig'ilishda odob-axloq, kiyinish madaniyati, o'zini tutish, maktab tartib-qoidalari va darslarga to'liq qatnashish intizomi haqida atroflicha muhokamalar o'tkazildi."
        ),
        'date': datetime(2026, 10, 13, 9, 25),
        'photo_url': "https://cdn4.telesco.pe/file/LoO8vJFqZSly7yhZ7uWbvmqEid3XHfWZnMJ9ZREu8x5nlviFEW8Nmy7oGlT6kcPZMEpmJLvd5x8-PfxQ0B589fHd0oEhZVLRVYG_NF1GJ-PO73C3z9OORPGNEx4Yz1syIFCM84GnBFte8J92yftHP0ilXEi2B3655x7_bE3wpknzKEkBo3e27otASZ9XYuJ1eWEPzXV6LP7rQ-W2VrPDEo8pDe6LE_WGzkdgWoMi-Q0KBg8sRmT5PfAaF6wCTBlXD8ETfzyqCiaynpFuV7cRT6ibtWsWjqOjRvh0Syk037Cd3ntNINd-O0Jo4NpI11tXNBpkV2020GqpqXa9PzEa2g.jpg",
        'rel_photo': "news/covers/qizlar_yigilishi.jpg",
        'is_featured': True,
    },
    {
        'title': "3-A sinfida Tarbiya fanidan 'Dunyomizga nimalar xavf solmoqda' mavzusida ochiq dars bo'lib o'tdi",
        'slug': "3-a-sinfida-tarbiya-fanidan-ochiq-dars",
        'category': cat_talim,
        'excerpt': "Namangan tumani 19-sonli maktabning 3-A sinf o'quvchilari ishtirokida Tarbiya fanidan qiziqarli va interaktiv ochiq dars tashkil etildi.",
        'content': (
            "14.10.2026 kuni Namangan tumani 19-sonli maktabning 3-'A' sinf o'quvchilari ishtirokida Tarbiya fanidan 'Dunyomizga nimalar xavf solmoqda' mavzusida ochiq dars o'tkazildi.\n\n"
            "Ochiq darsda o'quvchilar tabiatni asrash, ekologik madaniyat, mehr-oqibat va tinchlikning qadriga yetish haqida o'z fikr va bilimlarini faol namoyon etdilar. Dars zamonaviy pedagogik texnologiyalar va ko'rgazmali vositalar yordamida yuqori saviyada olib borildi."
        ),
        'date': datetime(2026, 10, 14, 14, 35),
        'photo_url': "https://cdn4.telesco.pe/file/myd_0cMLAYCfNNggI1msJdzu5cFhzLt_ueALML-EHtruZmCHud1Zu8xflfvMGciUci-FLhsNPFUKYxU7jOprBN7raZHqlaaVwO4lN8_aPsJsY1F_6bAsmnW6WjSG-NsYsrBxxNEOkI7k_osyXvCKv7dy-Vt3c0kOBDDmx0tBoj6QnG37BmJnb27aOwflXaSmfxGR3TrWeRIxA0r6AsznCUyMErnz2-1mILe73thIJ41j2psSn17o25pEZIOtpYip4swHtuXa3Z1s6QUpxAHtlwcRRGb8V_en126vpcwfNsbxliWPih0o2F12U3lFj7I6vRA_8jwUYXoRczyotky7bw.jpg",
        'rel_photo': "news/covers/ochiq_dars_3a.jpg",
        'is_featured': True,
    },
]

for na in news_list:
    n_obj, _ = News.objects.get_or_create(slug=na['slug'])
    n_obj.title = na['title']
    n_obj.category = na['category']
    n_obj.excerpt = na['excerpt']
    n_obj.content = na['content']
    n_obj.status = 'published'
    n_obj.is_featured = na['is_featured']
    n_obj.published_at = na['date']
    n_obj.views_count = 168
    
    if na['photo_url']:
        p = download_image(na['photo_url'], na['rel_photo'])
        if p:
            n_obj.cover_image = p
    n_obj.save()
    print(f"[OK] News saved: {n_obj.title}")

print("\n=== 6. CREATING RICH GALLERY IMAGES ===")
gallery_list = [
    ("Kelajak soatida saylov jarayonlari", posts[0]['photos'][0] if len(posts[0]['photos']) > 0 else None, "events"),
    ("Rus tili darsidagi loyiha ishlari", posts[1]['photos'][1] if len(posts[1]['photos']) > 1 else None, "school"),
    ("Besh tashabbus Yengil atletika qizg'in bahslar", posts[4]['photos'][1] if len(posts[4]['photos']) > 1 else None, "sports"),
    ("Milliylik — Milliy liboslar kunidan lavhalar", posts[10]['photos'][0] if len(posts[10]['photos']) > 0 else None, "events"),
    ("Shaxmat-shashka musobaqalari", posts[12]['photos'][1] if len(posts[12]['photos']) > 1 else None, "sports"),
    ("Ustozlar kuni xonadonlarga tashrif", posts[18]['photos'][1] if len(posts[18]['photos']) > 1 else None, "events"),
    ("Shodiya Akramaliyevaning kitob taqdimoti", posts[35]['photos'][0] if len(posts[35]['photos']) > 0 else None, "events"),
    ("Profilaktika va davomat uchrashuvlari", posts[37]['photos'][1] if len(posts[37]['photos']) > 1 else None, "school"),
    ("Mustaqillik ijodiy ko'rgazmasi", posts[92]['photos'][1] if len(posts[92]['photos']) > 1 else None, "school"),
]

for idx, (title, p_url, cat) in enumerate(gallery_list):
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
            print(f"[OK] Gallery image: {title}")

print("\n=======================================================")
print("COMPREHENSIVE CHANNEL IMPORT FINISHED SUCCESSFULLY!")
print(f"Teachers: {Teacher.objects.count()} | News: {News.objects.count()} | Achievements: {Achievement.objects.count()} | Gallery: {GalleryImage.objects.count()}")
print("=======================================================")
