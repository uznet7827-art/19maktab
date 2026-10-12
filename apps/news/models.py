from django.db import models
from django.utils.text import slugify
from django.utils.translation import get_language
from django.urls import reverse


class NewsCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi (UZ)")
    name_ru = models.CharField(max_length=100, blank=True, verbose_name="Kategoriya nomi (RU)")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="Kategoriya nomi (EN)")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    color = models.CharField(max_length=7, default='#4F46E5', verbose_name="Rang kodi")

    class Meta:
        verbose_name = 'Yangilik toifasi'
        verbose_name_plural = 'Yangilik toifalari'
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class News(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Qoralama'),
        ('scheduled', 'Rejalashtirilgan'),
        ('published', "E'lon qilingan"),
        ('archived', 'Arxivlangan'),
    ]

    title = models.CharField(max_length=300, verbose_name="Sarlavha (UZ)")
    title_ru = models.CharField(max_length=300, blank=True, verbose_name="Sarlavha (RU)")
    title_en = models.CharField(max_length=300, blank=True, verbose_name="Sarlavha (EN)")
    slug = models.SlugField(max_length=320, unique=True, verbose_name="Slug")
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='news_items', verbose_name="Toifa")
    excerpt = models.TextField(max_length=500, verbose_name="Qisqa mazmun (UZ)")
    excerpt_ru = models.TextField(max_length=500, blank=True, verbose_name="Qisqa mazmun (RU)")
    excerpt_en = models.TextField(max_length=500, blank=True, verbose_name="Qisqa mazmun (EN)")
    content = models.TextField(verbose_name="Batafsil matn (UZ)")
    content_ru = models.TextField(blank=True, verbose_name="Batafsil matn (RU)")
    content_en = models.TextField(blank=True, verbose_name="Batafsil matn (EN)")
    cover_image = models.ImageField(upload_to='news/covers/', blank=True, null=True, verbose_name="Muqova rasmi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Holati")
    is_featured = models.BooleanField(default=False, verbose_name="Muhim yangilik")
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name="Rejalashtirilgan vaqt")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="E'lon qilingan vaqt")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Tahrirlangan vaqt")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar soni")

    class Meta:
        verbose_name = 'Yangilik'
        verbose_name_plural = 'Yangiliklar'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    @property
    def localized_title(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.title_ru:
            return self.title_ru
        if lang.startswith('en') and self.title_en:
            return self.title_en
        return self.title

    @property
    def localized_excerpt(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.excerpt_ru:
            return self.excerpt_ru
        if lang.startswith('en') and self.excerpt_en:
            return self.excerpt_en
        return self.excerpt

    @property
    def localized_content(self):
        lang = get_language() or 'uz'
        if lang.startswith('ru') and self.content_ru:
            return self.content_ru
        if lang.startswith('en') and self.content_en:
            return self.content_en
        return self.content

    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'news'
            candidate_slug = base_slug
            idx = 1
            while News.objects.filter(slug=candidate_slug).exclude(pk=self.pk).exists():
                candidate_slug = f"{base_slug}-{idx}"
                idx += 1
            self.slug = candidate_slug
        super().save(*args, **kwargs)


class NewsImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='images', verbose_name="Yangilik")
    image = models.ImageField(upload_to='news/gallery/', verbose_name="Rasm")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Rasm izohi")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")

    class Meta:
        verbose_name = 'Yangilik rasmi'
        verbose_name_plural = 'Yangilik rasmlari'
        ordering = ['order', 'id']

    def __str__(self):
        return f"Rasm: {self.news.title[:30]}"


class NewsVideo(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='videos', verbose_name="Yangilik")
    title = models.CharField(max_length=200, verbose_name="Video nomi")
    video_file = models.FileField(upload_to='news/videos/', blank=True, verbose_name="Video fayl")
    youtube_url = models.URLField(blank=True, verbose_name="YouTube havolasi")
    thumbnail = models.ImageField(upload_to='news/video_thumbs/', blank=True, verbose_name="Video muqovasi")

    class Meta:
        verbose_name = 'Yangilik videosi'
        verbose_name_plural = 'Yangilik videolari'

    def __str__(self):
        return self.title


class NewsDocument(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='documents', verbose_name="Yangilik")
    title = models.CharField(max_length=200, verbose_name="Hujjat nomi")
    file = models.FileField(upload_to='news/documents/', verbose_name="Hujjat fayli")

    class Meta:
        verbose_name = 'Yangilik hujjati'
        verbose_name_plural = 'Yangilik hujjatlari'

    def __str__(self):
        return self.title
