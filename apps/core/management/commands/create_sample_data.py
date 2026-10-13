from django.core.management.base import BaseCommand
from apps.core.models import SiteSettings, Statistic, SchoolHistory
from apps.news.models import NewsCategory
from apps.teachers.models import Department, Teacher


class Command(BaseCommand):
    help = "Initializes sample data for 19-maktab (School #19 in Uzbekistan)"

    def handle(self, *args, **options):
        self.stdout.write("Initializing 19-maktab sample data...")

        # 1. SiteSettings
        site_settings, created = SiteSettings.objects.get_or_create(
            id=1,
            defaults={
                'school_name': "19-umumiy o'rta ta'lim maktabi",
                'school_name_ru': "Общеобразовательная школа №19",
                'school_name_en': "Secondary School #19",
                'tagline': "Sifatli ta'lim, yorqin kelajak poydevori!",
                'tagline_ru': "Качественное образование — фундамент яркого будущего!",
                'tagline_en': "Quality education is the foundation of a bright future!",
                'about_text': (
                    "19-umumiy o'rta ta'lim maktabi zamonaviy ta'lim standartlariga mos, "
                    "yuksak ma'naviyatli, chuqur bilimli yoshlarni tarbiyalashni o'z oldiga maqsad qilib qo'ygan. "
                    "Maktabimizda barcha zamonaviy sharoitlar, fan laboratoriyalari, sport zallari va "
                    "zamonaviy axborot texnologiyalari bilan jihozlangan sinfxonalar mavjud."
                ),
                'about_text_ru': (
                    "Общеобразовательная школа №19 ставит своей целью воспитание всесторонне "
                    "развитого молодого поколения в соответствии с современными стандартами. "
                    "В нашей школе созданы все условия: научные лаборатории, спортивные залы и "
                    "современные компьютерные классы."
                ),
                'about_text_en': (
                    "Secondary School #19 aims to foster a well-rounded and knowledgeable young generation "
                    "according to modern educational standards. Our school is equipped with state-of-the-art "
                    "laboratories, sports complexes, and IT classrooms."
                ),
                'director_name': "M. Nabiyeva",
                'director_photo': "director/director.png",
                'director_message': (
                    "Bizning 19-umumiy o'rta ta'lim maktabimiz har bir o'quvchining qobiliyati va iqtidorini ro'yobga chiqarish, "
                    "yoshlarni qonunlarga hurmat, yuksak ma'naviyat va zamonaviy ilm-fan ruhida tarbiyalashni bosh maqsad qilib qo'ygan. "
                    "Maktabimiz eshiklari barcha yoshlarimiz uchun yuksak marralar va orzular sari hamisha ochiqdir!"
                ),
                'phone': "+998 69 227-19-19",
                'email': "info@maktab19.uz",
                'address': "Namangan viloyati, Namangan tumani, 19-sonli umumiy o'rta ta'lim maktabi",
                'address_ru': "Наманганская область, Наманганский район, общеобразовательная школа №19",
                'address_en': "Namangan region, Namangan district, Secondary School #19",
                'working_hours': "Dushanba - Shanba: 08:00 - 18:00",
                'facebook_url': "https://facebook.com",
                'telegram_url': "https://t.me/qwert19idum",
                'instagram_url': "https://instagram.com",
                'youtube_url': "https://youtube.com",
                'primary_color': "#4F46E5",
                'secondary_color': "#06B6D4",
                'accent_color': "#FACC15",
            }
        )
        if not site_settings.director_photo:
            site_settings.director_photo = "director/director.png"
            site_settings.save()
        if created:
            self.stdout.write(self.style.SUCCESS("[OK] SiteSettings created."))
        else:
            self.stdout.write("SiteSettings already exists.")

        # 2. Statistics (4 items)
        stats_data = [
            {
                'title': "O'quvchilar soni",
                'title_ru': "Количество учеников",
                'title_en': "Total Students",
                'value': "1,450+",
                'icon': "fa-user-graduate",
                'order': 1,
            },
            {
                'title': "Malakali ustozlar",
                'title_ru': "Опытные учителя",
                'title_en': "Qualified Teachers",
                'value': "85+",
                'icon': "fa-chalkboard-teacher",
                'order': 2,
            },
            {
                'title': "Zamonaviy sinfxonalar",
                'title_ru': "Современные классы",
                'title_en': "Modern Classrooms",
                'value': "48",
                'icon': "fa-school",
                'order': 3,
            },
            {
                'title': "Yutuqlar va medallar",
                'title_ru': "Достижения и медали",
                'title_en': "Achievements & Medals",
                'value': "120+",
                'icon': "fa-trophy",
                'order': 4,
            },
        ]
        for s in stats_data:
            stat, _ = Statistic.objects.get_or_create(
                title=s['title'],
                defaults=s
            )
        self.stdout.write(self.style.SUCCESS("[OK] 4 Statistics initialized."))

        # 3. School History items
        history_data = [
            {
                'year': "1985",
                'title': "Maktabning tashkil etilishi",
                'title_ru': "Основание школы",
                'title_en': "Establishment of the School",
                'description': "19-maktab o'z faoliyatini 300 nafar o'quvchi bilan boshlagan.",
                'description_ru': "Школа №19 начала свою работу с 300 учащимися.",
                'description_en': "School #19 started its educational journey with 300 students.",
                'order': 1,
            },
            {
                'year': "2010",
                'title': "Zamonaviy rekonstruksiya",
                'title_ru': "Капитальная реконструкция",
                'title_en': "Major Modernization",
                'description': "Maktab binosi to'liq ta'mirlanib, yangi sport majmuasi foydalanishga topshirildi.",
                'description_ru': "Здание школы было полностью отремонтировано и открыт спорткомплекс.",
                'description_en': "Complete reconstruction with a newly equipped sports arena.",
                'order': 2,
            },
            {
                'year': "2022",
                'title': "Raqamli ta'lim tizimi",
                'title_ru': "Цифровизация образования",
                'title_en': "Digital Education Initiative",
                'description': "Barcha sinflar interaktiv doskalar va kompyuter texnologiyalari bilan jihozlandi.",
                'description_ru': "Все классы оборудованы интерактивными досками и ПК.",
                'description_en': "All classrooms upgraded with interactive smart boards and IT equipment.",
                'order': 3,
            },
        ]
        for h in history_data:
            SchoolHistory.objects.get_or_create(year=h['year'], defaults=h)
        self.stdout.write(self.style.SUCCESS("[OK] School history items initialized."))

        # 4. News Categories
        categories_data = [
            {'name': "Yangiliklar", 'name_ru': "Новости", 'name_en': "News", 'slug': "yangiliklar", 'color': "#4F46E5"},
            {'name': "Sport", 'name_ru': "Спорт", 'name_en': "Sports", 'slug': "sport", 'color': "#10B981"},
            {'name': "Fan-texnika", 'name_ru': "Наука и технологии", 'name_en': "Science & Tech", 'slug': "fan-texnika", 'color': "#F59E0B"},
        ]
        for c in categories_data:
            NewsCategory.objects.get_or_create(slug=c['slug'], defaults=c)
        self.stdout.write(self.style.SUCCESS("[OK] 3 News Categories initialized."))

        # 5. Departments & Teachers
        dept_exact, _ = Department.objects.get_or_create(
            name="Aniq fanlar",
            defaults={'name_ru': "Точные науки", 'name_en': "Exact Sciences"}
        )
        dept_human, _ = Department.objects.get_or_create(
            name="Ijtimoiy-gumanitar fanlar",
            defaults={'name_ru': "Гуманитарные науки", 'name_en': "Humanities"}
        )
        dept_lang, _ = Department.objects.get_or_create(
            name="Xorijiy tillar",
            defaults={'name_ru': "Иностранные языки", 'name_en': "Foreign Languages"}
        )

        teachers_data = [
            {
                'full_name': "Abdullayev Rustam Shokirovich",
                'subject': "Matematika va Informatika",
                'subject_ru': "Математика и Информатика",
                'subject_en': "Mathematics & Computer Science",
                'position': "Oliy toifali o'qituvchi",
                'position_ru': "Учитель высшей категории",
                'position_en': "Senior Master Teacher",
                'bio': "15 yildan ortiq pedagogik tajribaga ega. Olimpiada g'oliblarining ustozi.",
                'bio_ru': "Более 15 лет педагогического стажа. Наставник победителей олимпиад.",
                'bio_en': "Over 15 years of teaching experience. Mentor of Olympiad medalists.",
                'department': dept_exact,
                'experience_years': 15,
                'education': "O'zbekiston Milliy Universiteti, Magistr",
                'is_active': True,
                'is_featured': True,
                'order': 1,
                'email': "r.abdullayev@maktab19.uz",
            },
            {
                'full_name': "Sobirova Dilnoza Erkinovna",
                'subject': "Ona tili va adabiyot",
                'subject_ru': "Родной язык и литература",
                'subject_en': "Native Language & Literature",
                'position': "Yetakchi o'qituvchi",
                'position_ru': "Ведущий учитель",
                'position_en': "Lead Teacher",
                'bio': "Xalq ta'limi a'lochisi ko'krak nishoni sohibi.",
                'bio_ru': "Отличник народного образования.",
                'bio_en': "Excellence in Public Education award holder.",
                'department': dept_human,
                'experience_years': 12,
                'education': "Nizomiy nomidagi Toshkent davlat pedagogika universiteti",
                'is_active': True,
                'is_featured': True,
                'order': 2,
                'email': "d.sobirova@maktab19.uz",
            },
            {
                'full_name': "Usmonov Jasur Alisherovich",
                'subject': "Ingliz tili",
                'subject_ru': "Английский язык",
                'subject_en': "English Language",
                'position': "I toifali o'qituvchi",
                'position_ru': "Учитель 1-й категории",
                'position_en': "Level 1 Teacher",
                'bio': "IELTS 8.5 sohibi, xalqaro TESOL sertifikati egasi.",
                'bio_ru': "Обладатель IELTS 8.5 и международного сертификата TESOL.",
                'bio_en': "IELTS 8.5 and certified TESOL instructor.",
                'department': dept_lang,
                'experience_years': 8,
                'education': "O'zbekiston Davlat Jahon Tillari Universiteti",
                'is_active': True,
                'is_featured': True,
                'order': 3,
                'email': "j.usmonov@maktab19.uz",
            },
        ]

        for t in teachers_data:
            Teacher.objects.get_or_create(full_name=t['full_name'], defaults=t)
        self.stdout.write(self.style.SUCCESS("[OK] 3 Sample teachers initialized."))

        # 6. Sample Achievements (O'quvchilar yutuqlari)
        from apps.achievements.models import Achievement
        from django.utils import timezone
        import datetime

        achievements_data = [
            {
                'student_name': "Bekzod Rahimov",
                'grade': "11-A",
                'achievement_type': "olympiad",
                'title': "Matematika fanidan Respublika olimpiadasi mutlaq g'olibi",
                'title_ru': "Абсолютный победитель Республиканской олимпиады по математике",
                'title_en': "Absolute Winner of the National Mathematics Olympiad",
                'description': "19-maktab 11-sinf o'quvchisi Bekzod Rahimov Respublika bosqichida 1-o'rinni qo'lga kiritib, oltin medal bilan taqdirlandi.",
                'date': datetime.date(2026, 3, 20),
                'place': "1-o'rin",
                'is_active': True,
                'parent_consent': True,
            },
            {
                'student_name': "Madina Karimova",
                'grade': "9-B",
                'achievement_type': "science",
                'title': "Yosh dasturchilar IT-chempionati 1-o'rin sohibasi",
                'title_ru': "1-е место на Чемпионате молодых IT-разработчиков",
                'title_en': "1st Place Winner at Young Coders IT Championship",
                'description': "Sun'iy intellekt va robototexnika yo'nalishida yaratgan ta'lim loyihasi eng yuqori baholandi.",
                'date': datetime.date(2026, 4, 15),
                'place': "1-o'rin",
                'is_active': True,
                'parent_consent': True,
            },
            {
                'student_name': "Sardor Umarov",
                'grade': "10-V",
                'achievement_type': "sport",
                'title': "Shaxmat bo'yicha Toshkent shahar birinchiligi chempioni",
                'title_ru': "Чемпион Ташкента по шахматам среди юниоров",
                'title_en': "Tashkent City Junior Chess Champion",
                'description': "Barcha turda g'alaba qozonib, sport ustaligiga nomzod talabini bajardi.",
                'date': datetime.date(2026, 5, 10),
                'place': "1-o'rin",
                'is_active': True,
                'parent_consent': True,
            },
            {
                'student_name': "Shahlo Aliyeva",
                'grade': "8-A",
                'achievement_type': "art",
                'title': "\"Iste'dodli yoshlar\" respublika rasmlar ko'rik-tanlovi g'olibi",
                'title_ru': "Победитель республиканского конкурса рисунков 'Талантливая молодежь'",
                'title_en': "Winner of the National Youth Art Contest",
                'description': "\"Yangi O'zbekiston yoshlari\" mavzusidagi ijodiy ishi eng yaxshi deb topildi.",
                'date': datetime.date(2026, 2, 28),
                'place': "2-o'rin",
                'is_active': True,
                'parent_consent': True,
            },
        ]
        for a in achievements_data:
            Achievement.objects.get_or_create(student_name=a['student_name'], title=a['title'], defaults=a)
        self.stdout.write(self.style.SUCCESS("[OK] 4 Sample achievements initialized."))

        # 7. Sample News (Yangiliklar)
        from apps.news.models import News
        cat_yangiliklar = NewsCategory.objects.filter(slug='yangiliklar').first()
        cat_sport = NewsCategory.objects.filter(slug='sport').first()
        cat_fantech = NewsCategory.objects.filter(slug='fan-texnika').first()

        sample_news_list = [
            {
                'title': "19-maktabda zamonaviy STEM laboratoriyasi ochildi",
                'title_ru': "В школе №19 открылась современная STEM-лаборатория",
                'title_en': "Modern STEM Laboratory Opened at School #19",
                'slug': "stem-laboratoriyasi-ochildi",
                'category': cat_fantech,
                'excerpt': "Maktabimizda o'quvchilarning ilmiy salohiyatini oshirish uchun yangi avlod STEM laboratoriyasi ishga tushirildi.",
                'content': "Maktab ma'muriyati tashabbusi bilan yangi STEM va robototexnika sinfi jihozlandi. Bu yerda o'quvchilar amaliy tajribalar o'tkazishlari mumkin.",
                'status': 'published',
                'is_featured': True,
                'published_at': timezone.now() - datetime.timedelta(days=2),
            },
            {
                'title': "O'quvchilarimiz shaxmat turnirida mutlaq g'olib bo'lishdi",
                'title_ru': "Наши ученики одержали абсолютную победу в шахматном турнире",
                'title_en': "Our Students Achieved Total Victory in Chess Tournament",
                'slug': "shaxmat-turnirida-goliblik",
                'category': cat_sport,
                'excerpt': "Tumanlararo maktablar o'rtasida o'tkazilgan shaxmat bahslarida 19-maktab terma jamoasi bosh sovrinni qo'lga kiritdi.",
                'content': "Murosasiz kechgan bahslarda maktabimiz jamoasi faxrli 1-o'rinni egallab, shahar bosqichiga yo'llanma oldi.",
                'status': 'published',
                'is_featured': True,
                'published_at': timezone.now() - datetime.timedelta(days=5),
            },
            {
                'title': "\"Kitobxon maktab\" haftaligi doirasida adabiy kecha bo'lib o'tdi",
                'title_ru': "Литературный вечер в рамках недели 'Читающая школа'",
                'title_en': "Literary Evening as Part of the 'Reading School' Week",
                'slug': "kitobxon-maktab-haftaligi",
                'category': cat_yangiliklar,
                'excerpt': "Maktab axborot-resurs markazida mashhur yozuvchi va shoirlar ishtirokida ma'naviy-ma'rifiy uchrashuv o'tkazildi.",
                'content': "Tadbirda faol kitobxon o'quvchilar qimmatbaho sovg'alar va badiiy kitoblar jamlanmasi bilan taqdirlandi.",
                'status': 'published',
                'is_featured': True,
                'published_at': timezone.now() - datetime.timedelta(days=8),
            },
        ]
        for n in sample_news_list:
            News.objects.get_or_create(slug=n['slug'], defaults=n)
        self.stdout.write(self.style.SUCCESS("[OK] 3 Sample news initialized."))

        try:
            import import_comprehensive_channel_data
            self.stdout.write(self.style.SUCCESS("[OK] Comprehensive channel data imported."))
        except Exception as e:
            self.stdout.write(f"Comprehensive channel data import note: {e}")

        self.stdout.write(self.style.SUCCESS("All sample data created successfully!"))

