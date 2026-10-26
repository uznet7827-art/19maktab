from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import SiteSettings, Statistic, GalleryImage, SchoolHistory
from apps.news.models import News, NewsCategory, NewsImage, NewsVideo, NewsDocument
from apps.teachers.models import Teacher, Department
from apps.achievements.models import Achievement
from apps.contacts.models import Contact


class Command(BaseCommand):
    help = "Resets all site data for a clean slate, preserving admin user."

    def handle(self, *args, **options):
        self.stdout.write("Barcha ma'lumotlarni tozalash boshlandi...")

        # 1. Clean News
        NewsImage.objects.all().delete()
        NewsVideo.objects.all().delete()
        NewsDocument.objects.all().delete()
        News.objects.all().delete()
        NewsCategory.objects.all().delete()
        self.stdout.write("[OK] Yangiliklar va kategoriyalar tozalandi.")

        # 2. Clean Teachers
        Teacher.objects.all().delete()
        Department.objects.all().delete()
        self.stdout.write("[OK] O'qituvchilar va kafedralar tozalandi.")

        # 3. Clean Achievements
        Achievement.objects.all().delete()
        self.stdout.write("[OK] Yutuqlar tozalandi.")

        # 4. Clean Core
        GalleryImage.objects.all().delete()
        SchoolHistory.objects.all().delete()
        Statistic.objects.all().delete()
        self.stdout.write("[OK] Galereya, maktab tarixi va statistika tozalandi.")

        # 5. Clean Contacts
        Contact.objects.all().delete()
        self.stdout.write("[OK] Murojaatlar tozalandi.")

        # 6. Reset SiteSettings
        site = SiteSettings.objects.first()
        if not site:
            site = SiteSettings.objects.create(school_name="19-sonli umumiy o'rta ta'lim maktabi")
        site.school_name = "19-sonli umumiy o'rta ta'lim maktabi"
        site.school_name_ru = "Общеобразовательная школа №19"
        site.school_name_en = "Secondary School No. 19"
        site.tagline = "Kelajak sari birinchi qadam"
        site.tagline_ru = "Первый шаг в будущее"
        site.tagline_en = "First step towards the future"
        site.about_text = ""
        site.about_text_ru = ""
        site.about_text_en = ""
        site.director_name = ""
        site.director_message = ""
        site.phone = "+998 69 227-00-19"
        site.email = "19-maktab@namangan.uz"
        site.address = "Namangan viloyati, Namangan tumani, Qumqo'rg'on MFY, Mullakudung qishlog'i"
        site.telegram_url = "https://t.me/qwert19idum"
        site.hero_image = None
        site.director_photo = None
        site.save()
        self.stdout.write("[OK] Asosiy sayt sozlamalari yangilandi.")

        # 7. Ensure admin user exists
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin', 'admin@maktab19.uz', 'Admin123!')
            self.stdout.write(self.style.SUCCESS("[OK] Admin foydalanuvchisi yaratildi: login 'admin', parol 'Admin123!'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"[OK] Admin hisobi saqlandi: {admin_user.username}"))

        self.stdout.write(self.style.SUCCESS("Sayt to'liq tozalandi!"))
