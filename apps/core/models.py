from django.db import models
from django.utils.translation import get_language


class SiteSettings(models.Model):
    school_name = models.CharField(max_length=200, verbose_name="Maktab nomi (UZ)")
    school_name_ru = models.CharField(max_length=200, blank=True, verbose_name="Maktab nomi (RU)")
    school_name_en = models.CharField(max_length=200, blank=True, verbose_name="Maktab nomi (EN)")
    tagline = models.CharField(max_length=300, blank=True, verbose_name="Shior (UZ)")
    tagline_ru = models.CharField(max_length=300, blank=True, verbose_name="Shior (RU)")
    tagline_en = models.CharField(max_length=300, blank=True, verbose_name="Shior (EN)")
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Bosh sahifa rasmi")
    about_text = models.TextField(blank=True, verbose_name="Maktab haqida (UZ)")
    about_text_ru = models.TextField(blank=True, verbose_name="Maktab haqida (RU)")
    about_text_en = models.TextField(blank=True, verbose_name="Maktab haqida (EN)")
    director_name = models.CharField(max_length=200, blank=True, verbose_name="Direktor F.I.Sh")
    director_message = models.TextField(blank=True, verbose_name="Direktor murojaati")
    director_photo = models.ImageField(upload_to='director/', blank=True, null=True, verbose_name="Direktor rasmi")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon raqam")
    email = models.EmailField(blank=True, verbose_name="Elektron pochta")
    address = models.TextField(blank=True, verbose_name="Manzil (UZ)")
    address_ru = models.TextField(blank=True, verbose_name="Manzil (RU)")
    address_en = models.TextField(blank=True, verbose_name="Manzil (EN)")
    working_hours = models.CharField(max_length=200, blank=True, verbose_name="Ish vaqti")
    facebook_url = models.URLField(blank=True, verbose_name="Facebook havolasi")
    telegram_url = models.URLField(blank=True, verbose_name="Telegram havolasi")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram havolasi")
    youtube_url = models.URLField(blank=True, verbose_name="YouTube havolasi")
    
    # Colors
    primary_color = models.CharField(max_length=7, default='#4F46E5', verbose_name="Asosiy rang")
    secondary_color = models.CharField(max_length=7, default='#06B6D4', verbose_name="Qo'shimcha rang")
    accent_color = models.CharField(max_length=7, default='#FACC15', verbose_name="Urg'u rangi")
    
    class Meta:
        verbose_name = 'Sayt sozlamalari'
        verbose_name_plural = 'Sayt sozlamalari'

    def __str__(self):
        return self.school_name or "19-maktab sayt sozlamalari"

    @property
    def localized_name(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.school_name_ru:
            return self.school_name_ru
        if lang.startswith('en') and self.school_name_en:
            return self.school_name_en
        return self.school_name

    @property
    def localized_tagline(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.tagline_ru:
            return self.tagline_ru
        if lang.startswith('en') and self.tagline_en:
            return self.tagline_en
        return self.tagline

    @property
    def localized_about(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.about_text_ru:
            return self.about_text_ru
        if lang.startswith('en') and self.about_text_en:
            return self.about_text_en
        return self.about_text

    @property
    def localized_address(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.address_ru:
            return self.address_ru
        if lang.startswith('en') and self.address_en:
            return self.address_en
        return self.address


class Statistic(models.Model):
    title = models.CharField(max_length=100, verbose_name="Sarlavha (UZ)")
    title_ru = models.CharField(max_length=100, blank=True, verbose_name="Sarlavha (RU)")
    title_en = models.CharField(max_length=100, blank=True, verbose_name="Sarlavha (EN)")
    value = models.CharField(max_length=50, verbose_name="Qiymat")  # e.g. '1200+', '95%'
    icon = models.CharField(max_length=50, default='fa-users', verbose_name="Ikonka (FontAwesome yoki SVG)")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = 'Statistika'
        verbose_name_plural = 'Statistikalar'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title}: {self.value}"

    @property
    def localized_title(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.title_ru:
            return self.title_ru
        if lang.startswith('en') and self.title_en:
            return self.title_en
        return self.title


class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('school', 'Maktab'),
        ('events', 'Tadbirlar'),
        ('sports', 'Sport'),
        ('other', 'Boshqa'),
    ]
    title = models.CharField(max_length=200, verbose_name="Rasm nomi")
    image = models.ImageField(upload_to='gallery/', verbose_name="Rasm fayli")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='school', verbose_name="Kategoriya")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuklangan vaqti")

    class Meta:
        verbose_name = 'Galereya rasmi'
        verbose_name_plural = 'Galereya rasmlari'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class SchoolHistory(models.Model):
    year = models.CharField(max_length=10, verbose_name="Yil")
    title = models.CharField(max_length=200, verbose_name="Sarlavha (UZ)")
    title_ru = models.CharField(max_length=200, blank=True, verbose_name="Sarlavha (RU)")
    title_en = models.CharField(max_length=200, blank=True, verbose_name="Sarlavha (EN)")
    description = models.TextField(verbose_name="Tavsif (UZ)")
    description_ru = models.TextField(blank=True, verbose_name="Tavsif (RU)")
    description_en = models.TextField(blank=True, verbose_name="Tavsif (EN)")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")

    class Meta:
        verbose_name = 'Maktab tarixi'
        verbose_name_plural = 'Maktab tarixi bosqichlari'
        ordering = ['order', 'year']

    def __str__(self):
        return f"{self.year} - {self.title}"

    @property
    def localized_title(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.title_ru:
            return self.title_ru
        if lang.startswith('en') and self.title_en:
            return self.title_en
        return self.title

    @property
    def localized_description(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.description_ru:
            return self.description_ru
        if lang.startswith('en') and self.description_en:
            return self.description_en
        return self.description
