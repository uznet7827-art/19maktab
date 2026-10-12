from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import NewsCategory, News, NewsImage, NewsVideo, NewsDocument


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    fields = ('thumbnail_preview', 'image', 'caption', 'order')
    readonly_fields = ('thumbnail_preview',)

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover;" />', obj.image.url)
        return "-"
    thumbnail_preview.short_description = "Oldindan ko'rish"


class NewsVideoInline(admin.TabularInline):
    model = NewsVideo
    extra = 0
    fields = ('title', 'youtube_url', 'video_file', 'thumbnail')


class NewsDocumentInline(admin.TabularInline):
    model = NewsDocument
    extra = 0
    fields = ('title', 'file')


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ru', 'name_en', 'slug', 'color_badge')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'name_ru', 'name_en')

    def color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            obj.color,
            obj.color
        )
    color_badge.short_description = "Rang"


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('cover_thumbnail', 'title', 'category', 'status_badge', 'is_featured', 'published_at', 'views_count')
    list_filter = ('status', 'category', 'is_featured', 'published_at', 'created_at')
    search_fields = ('title', 'title_ru', 'title_en', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    inlines = [NewsImageInline, NewsVideoInline, NewsDocumentInline]
    actions = ['make_published', 'make_archived']

    fieldsets = (
        ("Sarlavhalar va toifa", {
            'fields': (
                ('title', 'title_ru', 'title_en'),
                ('slug', 'category'),
                'cover_image',
            )
        }),
        ("Qisqa mazmun", {
            'fields': (
                'excerpt',
                'excerpt_ru',
                'excerpt_en',
            )
        }),
        ("To'liq matn", {
            'fields': (
                'content',
                'content_ru',
                'content_en',
            )
        }),
        ("Holat va sana", {
            'fields': (
                ('status', 'is_featured'),
                ('scheduled_at', 'published_at'),
                'views_count',
            )
        }),
    )

    def cover_thumbnail(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;" />', obj.cover_image.url)
        return "-"
    cover_thumbnail.short_description = "Muqova"

    def status_badge(self, obj):
        colors = {
            'draft': '#6B7280',
            'scheduled': '#3B82F6',
            'published': '#10B981',
            'archived': '#EF4444',
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 7px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Holat"

    @admin.action(description="Tanlangan yangiliklarni e'lon qilish")
    def make_published(self, request, queryset):
        rows_updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f"{rows_updated} ta yangilik muvaffaqiyatli e'lon qilindi.")

    @admin.action(description="Tanlangan yangiliklarni arxivlash")
    def make_archived(self, request, queryset):
        rows_updated = queryset.update(status='archived')
        self.message_user(request, f"{rows_updated} ta yangilik arxivlandi.")
