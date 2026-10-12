from django.db import models
from django.utils.translation import get_language


class Achievement(models.Model):
    TYPE_CHOICES = [
        ('olympiad', 'Olimpiada'),
        ('sport', 'Sport'),
        ('art', "San'at"),
        ('science', 'Fan'),
        ('other', 'Boshqa'),
    ]

    student_name = models.CharField(max_length=200, verbose_name="O'quvchi ismi-familiyasi")
    grade = models.CharField(max_length=20, blank=True, verbose_name="Sinfi")
    achievement_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Yutuq turi")
    title = models.CharField(max_length=300, verbose_name="Yutuq nomi / Musobaqa (UZ)")
    title_ru = models.CharField(max_length=300, blank=True, verbose_name="Yutuq nomi (RU)")
    title_en = models.CharField(max_length=300, blank=True, verbose_name="Yutuq nomi (EN)")
    description = models.TextField(blank=True, verbose_name="Batafsil ma'lumot")
    photo = models.ImageField(upload_to='achievements/', blank=True, null=True, verbose_name="Fotosurat")
    date = models.DateField(verbose_name="Erishilgan sana")
    place = models.CharField(max_length=20, blank=True, verbose_name="Egallagan o'rni")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")
    parent_consent = models.BooleanField(
        default=False,
        verbose_name="Ota-ona roziligi (Surat va ma'lumotlarni e'lon qilish uchun)"
    )

    class Meta:
        verbose_name = 'O\'quvchi yutug\'i'
        verbose_name_plural = 'O\'quvchilar yutuqlari'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.student_name} - {self.title} ({self.place or self.get_achievement_type_display()})"

    @property
    def localized_title(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.title_ru:
            return self.title_ru
        if lang.startswith('en') and self.title_en:
            return self.title_en
        return self.title
