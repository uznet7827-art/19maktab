from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, Statistic, GalleryImage, SchoolHistory


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': (
                ('school_name', 'school_name_ru', 'school_name_en'),
                ('tagline', 'tagline_ru', 'tagline_en'),
                'hero_image',
            )
        }),
        ("Direktor ma'lumotlari", {
            'fields': (
                'director_name',
                'director_message',
                'director_photo',
            )
        }),
        ("Maktab haqida matn", {
            'fields': (
                'about_text',
                'about_text_ru',
                'about_text_en',
            )
        }),
        ("Aloqa ma'lumotlari", {
            'fields': (
                ('phone', 'email'),
                'working_hours',
                ('address', 'address_ru', 'address_en'),
            )
        }),
        ("Ijtimoiy tarmoqlar", {
            'fields': (
                ('facebook_url', 'telegram_url'),
                ('instagram_url', 'youtube_url'),
            )
        }),
        ("Sayt dizayn ranglari", {
            'fields': (
                ('primary_color', 'secondary_color', 'accent_color'),
            )
        }),
    )

    def has_add_permission(self, request):
        # Only allow 1 instance of SiteSettings
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('title', 'value', 'icon', 'order', 'is_active')
    list_editable = ('value', 'order', 'is_active')
    search_fields = ('title', 'title_ru', 'title_en', 'value')
    list_filter = ('is_active',)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'title', 'category', 'order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title',)
    list_editable = ('category', 'order', 'is_active')

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height: 45px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "-"
    thumbnail_preview.short_description = "Rasm"


@admin.register(SchoolHistory)
class SchoolHistoryAdmin(admin.ModelAdmin):
    list_display = ('year', 'title', 'order')
    list_editable = ('order',)
    search_fields = ('year', 'title', 'description')
    ordering = ('order', 'year')
