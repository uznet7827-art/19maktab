# 19-Maktab — Maktab Veb-sayti Backend Platformasi (School #19 in Uzbekistan)

Ushbu loyiha O'zbekistondagi 19-umumiy o'rta ta'lim maktabi uchun ishlab chiqilgan zamonaviy, xavfsiz va ko'p tilli (O'zbek, Rus, Ingliz) Django veb-platformasi backend tizimidir.

---

## 🚀 Asosiy Imkoniyatlar va Arxitektura

- **Ko'p tillilik (Multi-language)**: Sayt 3 ta tilda to'liq ishlaydi (`uz` - O'zbek, `ru` - Русский, `en` - English). Dinamik til o'zgartirish sessiyalar va kuki orqali qo'llab-quvvatlanadi (`/api/set-language/`).
- **Ilovalar modullari (`apps/`)**:
  - `core`: Saytning global sozlamalari (`SiteSettings`), ranglar sxemasi, maktab statistikasi (`Statistic`), tarixi (`SchoolHistory`) va fotogalereya (`GalleryImage`).
  - `news`: Toifalar (`NewsCategory`), maqolalar (`News`), rasmlar, videolar va rasmiy yuklab olinuvchi hujjatlar (`NewsDocument`). Karusel uchun maxsus JSON API (`/api/news/carousel/`).
  - `teachers`: O'qituvchilar va kafedralar (`Department`), pedagoglar profillari va tajribasi.
  - `contacts`: Qabul, taklif va shikoyatlar uchun aloqa shakli, **IP bo'yicha soatiga 3 ta murojaatdan oshmaslik cheklovi (Rate Limiting)** va admin javob berish moduli.
  - `achievements`: O'quvchilar yutuqlari (Olimpiada, sport, fan) va ota-onalar roziligi (`parent_consent`) nazorati.
- **Xavfsizlik**:
  - Barcha so'rovlarda CSRF himoyasi.
  - Murojaatlar uchun Rate Limiting (DoS va spamdan himoya).
  - Fayl yuklash hajmi va xavfsizligi chegaralangan.
  - Production xavfsizlik sozlamalari (`SECURE_BROWSER_XSS_FILTER`, `X_FRAME_OPTIONS`, SSL redirect imkoniyati).

---

## 📁 Loyiha Strukturasi

```
maktab19/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/          (Sayt sozlamalari, bosh sahifa, tarix, galereya)
│   ├── news/          (Yangiliklar, toifalar, fayllar, karusel API)
│   ├── teachers/      (Ustozlar, kafedralar)
│   ├── contacts/      (Aloqa formasi, rate limiting)
│   └── achievements/  (O'quvchilar yutuqlari)
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
├── media/
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── about.html
│   ├── contact.html
│   ├── gallery.html
│   ├── news/
│   │   ├── news_list.html
│   │   └── news_detail.html
│   ├── teachers/
│   │   ├── teacher_list.html
│   │   └── teacher_detail.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
└── locale/
    ├── uz/
    ├── ru/
    └── en/
```

---

## 🛠 O'rnatish va Ishga Tushirish

### 1. Muhitni tayyorlash
```bash
# Loyiha papkasiga o'tish
cd C:\Users\ibrohim\.gemini\antigravity\scratch\maktab19

# Virtual muhit yaratish va faollashtirish (ixtiyoriy, tavsiya etiladi)
python -m venv venv
# Windows:
.\venv\Scripts\activate

# Kutubxonalarni o'rnatish
pip install -r requirements.txt
```

### 2. Konfiguratsiya (.env)
`.env.example` faylidan nusxa olib, `.env` faylini sozlang:
```ini
SECRET_KEY=your-secure-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### 3. Migratsiyalar va Namuna Ma'lumotlarni Yuklash
```bash
# Migratsiyalarni yaratish va qo'llash
python manage.py makemigrations
python manage.py migrate

# Namuna ma'lumotlarni avtomatik yaratish
python manage.py create_sample_data

# Administrator foydalanuvchisini yaratish
python manage.py createsuperuser
```

### 4. Serverni ishga tushirish
```bash
python manage.py runserver
```
Veb-saytga kiring: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
Admin panel: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Testlarni Ishga Tushirish

Loyiha to'liq birlik (unit) va integratsion testlar bilan qoplangan:
```bash
python manage.py test apps.news apps.contacts
```

Testlar quyidagilarni avtomatik tekshiradi:
- Yangiliklar sahifasi 200 HTTP javob qaytarishi.
- Faqat e'lon qilingan yangiliklar ko'rinishi, qoralamalar ko'rinmasligi.
- Yangilik ochilganda `views_count` 1 ga oshishi.
- Karusel API (`/api/news/carousel/`) to'g'ri JSON formatda qaytishi.
- Aloqa formasi validatsiyasi va maxfiylik roziligi tekshiruvi.
- Soatiga 3 tadan ko'p so'rov yuborilganda 429 (Too Many Requests) qaytishi.

---

## 🌐 Asosiy URL Marshrutlari

| URL | Tavsif |
|---|---|
| `/` | Bosh sahifa (Sayt sozlamalari, statistika, yangiliklar, ustozlar, yutuqlar) |
| `/about/` | Maktab haqida va xronologik tarix |
| `/teachers/` | Ustozlar ro'yxati (Kafedra filtri va qidiruv) |
| `/teachers/<pk>/` | Ustozning batafsil profili |
| `/news/` | Yangiliklar ro'yxati (Toifalar filtri, qidiruv va sahifalash) |
| `/news/<slug>/` | Yangilikning to'liq matni, rasm/video/hujjatlar |
| `/gallery/` | Maktab fotogalereyasi (Bo'limlar filtri) |
| `/contact/` | Onlayn murojaat formasi (Rate limiting bilan) |
| `/api/news/carousel/` | Karusel uchun JSON ma'lumotlar |
| `/api/set-language/` | Tizim tilini o'zgartirish API |
| `/admin/` | Django boshqaruv paneli |
