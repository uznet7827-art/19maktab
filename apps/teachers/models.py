from django.db import models
from django.utils.translation import get_language
from django.urls import reverse


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kafedra / Yo'nalish nomi (UZ)")
    name_ru = models.CharField(max_length=100, blank=True, verbose_name="Kafedra nomi (RU)")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="Kafedra nomi (EN)")

    class Meta:
        verbose_name = 'Kafedra / Yo\'nalish'
        verbose_name_plural = 'Kafedralar'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def localized_name(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.name_ru:
            return self.name_ru
        if lang.startswith('en') and self.name_en:
            return self.name_en
        return self.name


class Teacher(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="F.I.Sh")
    subject = models.CharField(max_length=100, verbose_name="Dars beradigan fani (UZ)")
    subject_ru = models.CharField(max_length=100, blank=True, verbose_name="Fani (RU)")
    subject_en = models.CharField(max_length=100, blank=True, verbose_name="Fani (EN)")
    position = models.CharField(max_length=100, verbose_name="Lavozimi / Toifasi (UZ)")
    position_ru = models.CharField(max_length=100, blank=True, verbose_name="Lavozimi (RU)")
    position_en = models.CharField(max_length=100, blank=True, verbose_name="Lavozimi (EN)")
    bio = models.TextField(blank=True, verbose_name="Tarjimai hol / Qisqacha ma'lumot (UZ)")
    bio_ru = models.TextField(blank=True, verbose_name="Ma'lumot (RU)")
    bio_en = models.TextField(blank=True, verbose_name="Ma'lumot (EN)")
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True, verbose_name="Fotosurat")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='teachers', verbose_name="Kafedra")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="Ish staji (yil)")
    education = models.CharField(max_length=300, blank=True, verbose_name="Ma'lumoti")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_featured = models.BooleanField(default=False, verbose_name="Bosh sahifada ko'rsatish")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")
    email = models.EmailField(blank=True, verbose_name="Elektron pochta")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan sana")

    class Meta:
        verbose_name = 'O\'qituvchi'
        verbose_name_plural = 'O\'qituvchilar'
        ordering = ['order', 'full_name']

    def __str__(self):
        return f"{self.full_name} ({self.subject})"

    def get_absolute_url(self):
        return reverse('teachers:detail', kwargs={'pk': self.pk})

    @property
    def localized_subject(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.subject_ru:
            return self.subject_ru
        if lang.startswith('en') and self.subject_en:
            return self.subject_en
        return self.subject

    @property
    def localized_position(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.position_ru:
            return self.position_ru
        if lang.startswith('en') and self.position_en:
            return self.position_en
        return self.position

    @property
    def localized_bio(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.bio_ru:
            return self.bio_ru
        if lang.startswith('en') and self.bio_en:
            return self.bio_en
        return self.bio
