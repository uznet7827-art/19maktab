import os
import sys
import re
import requests
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.files.base import ContentFile
from apps.teachers.models import Department, Teacher
from apps.achievements.models import Achievement

def to_new_uzbek(t):
    if not t:
        return t
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

def setup_teachers_and_achievements():
    print("O'qituvchilar va yutuqlarni yangi lotin alifbosi bilan kiritish...")

    # Kafedralar
    d_aniq, _ = Department.objects.get_or_create(name=to_new_uzbek("Aniq fanlar kafedrasi"))
    d_tabiiy, _ = Department.objects.get_or_create(name=to_new_uzbek("Tabiiy fanlar kafedrasi"))
    d_gumanitar, _ = Department.objects.get_or_create(name=to_new_uzbek("Gumanitar va tillar kafedrasi"))
    d_boshlangich, _ = Department.objects.get_or_create(name=to_new_uzbek("Boşlanğiç ta'lim kafedrasi"))
    d_faxriy, _ = Department.objects.get_or_create(name=to_new_uzbek("Faxriy ustozlar"))

    # O'qituvchilar
    teachers_list = [
        {
            "full_name": "Axmadjanova Dilbarxon",
            "subject": to_new_uzbek("Matematika fani"),
            "position": to_new_uzbek("Oliy toifali matematika óqituvçisi"),
            "department": d_aniq,
            "bio": to_new_uzbek("Ko'p yillik tajribaga ega, óquvçilari tuman va viloyat olimpiadalarida muvaffaqiyatli qatnaşib kelayotgan fidoyi ustoz."),
            "experience_years": 22,
            "order": 1,
            "is_featured": True
        },
        {
            "full_name": "Filaydinova Umida",
            "subject": to_new_uzbek("Boşlanğiç sinf ta'limi"),
            "position": to_new_uzbek("Yetakçi boşlanğiç sinf óqituvçisi"),
            "department": d_boshlangich,
            "bio": to_new_uzbek("Kreativ dars uslublari, interfaol mashg'ulotlar va yosh bolalar tarbiyasi bo'yicha namunali pedagog."),
            "experience_years": 14,
            "order": 2,
            "is_featured": True
        },
        {
            "full_name": "Ismailova Mohiraxon",
            "subject": to_new_uzbek("Ingliz tili"),
            "position": to_new_uzbek("Ingliz tili fani óqituvçisi"),
            "department": d_gumanitar,
            "bio": to_new_uzbek("Óquvçilarga xalqaro til standartlari, zamonaviy metodikalar asosida xorijiy tillarni chuqur órganişga yordam beradi."),
            "experience_years": 12,
            "order": 3,
            "is_featured": True
        },
        {
            "full_name": "Ubaydullayev Hamidullo",
            "subject": to_new_uzbek("Ingliz tili (Faxriy ustoz)"),
            "position": to_new_uzbek("Faxriy pedagog"),
            "department": d_faxriy,
            "bio": to_new_uzbek("40 yildan ortiq vaqt davomida minglab yoshlarga ta'lim bergan, maktabning faxri bo'lgan ustoz."),
            "experience_years": 40,
            "order": 4,
            "is_featured": True
        },
        {
            "full_name": "Husanboyeva Dilnoza",
            "subject": to_new_uzbek("Musiqa madaniyati"),
            "position": to_new_uzbek("Musiqa fani óqituvçisi"),
            "department": d_gumanitar,
            "bio": to_new_uzbek("Maktabning iqtidorli yoshlarini musiqiy san'at va milliy qo'shiqchilikka yo'naltiruvchi tajribali murabbiy."),
            "experience_years": 16,
            "order": 5,
            "is_featured": True
        }
    ]

    for td in teachers_list:
        t, created = Teacher.objects.get_or_create(
            full_name=td["full_name"],
            defaults={
                "subject": td["subject"],
                "position": td["position"],
                "department": td["department"],
                "bio": td["bio"],
                "experience_years": td["experience_years"],
                "order": td["order"],
                "is_featured": td["is_featured"],
                "is_active": True
            }
        )
        if not created:
            t.subject = td["subject"]
            t.position = td["position"]
            t.bio = td["bio"]
            t.is_featured = True
            t.save()
        print(f"Teacher saved: {t.full_name}")

    # Yutuqlar (Achievements)
    achievements_list = [
        {
            "student_name": "Abdusattorova Nigora",
            "grade": "6-A",
            "title": to_new_uzbek("Kelajak yulduzlari oçiq olimpiadasi — Super oliy órin!"),
            "achievement_type": "olympiad",
            "description": to_new_uzbek("Ingliz tili fanidan Farg'ona viloyatida ótqazilgan xalqaro olimpiadada 'Super Oliy' órinni qo'lga kiritdi."),
            "date": date(2026, 10, 1),
            "place": "Super Oliy",
            "is_active": True
        },
        {
            "student_name": "Akramaliyeva Shodiya",
            "grade": "9-A",
            "title": to_new_uzbek("'Elning erka qiziman' kórrik-tanlovi ğolibi"),
            "achievement_type": "art",
            "description": to_new_uzbek("Iqtidorli óquvçimiz tuman miqyosida ótqazilgan 'Elning erka qiziman' ijodiy tanlovida 1-órinni egalladi."),
            "date": date(2026, 9, 25),
            "place": "1-o'rin",
            "is_active": True
        },
        {
            "student_name": "Tuman fan olimpiadasi g'oliblari jamoasi",
            "grade": "9-11 sinflar",
            "title": to_new_uzbek("Fan olimpiadasining tuman bosqiçida faxrli órinlar"),
            "achievement_type": "olympiad",
            "description": to_new_uzbek("Maktabimizning bir qator iqtidorli óquvçilari aniq va tabiiy fanlar olimpiadasining tuman bosqiçida faxrli órinlarni egallaşdi."),
            "date": date(2026, 11, 3),
            "place": "1-2-3 o'rinlar",
            "is_active": True
        }
    ]

    for ad in achievements_list:
        a, _ = Achievement.objects.get_or_create(
            student_name=ad["student_name"],
            defaults=ad
        )
        print(f"Achievement saved: {a.title}")

if __name__ == '__main__':
    setup_teachers_and_achievements()
