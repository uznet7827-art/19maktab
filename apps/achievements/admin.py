from django.contrib import admin
from django.utils.html import format_html
from .models import Achievement


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail_preview',
        'student_name',
        'grade',
        'achievement_type_badge',
        'title',
        'place',
        'date',
        'parent_consent_badge',
        'is_active',
    )
    list_filter = ('achievement_type', 'is_active', 'parent_consent', 'date')
    search_fields = ('student_name', 'title', 'title_ru', 'title_en', 'description', 'place')
    list_editable = ('is_active',)

    def thumbnail_preview(self, obj):
        if obj.photo and obj.parent_consent:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 6px;" />', obj.photo.url)
        elif obj.photo and not obj.parent_consent:
            return format_html('<span style="color: #EF4444; font-size: 11px;">⚠️ Rozilik yo\'q</span>')
        return "-"
    thumbnail_preview.short_description = "Surat"

    def achievement_type_badge(self, obj):
        colors = {
            'olympiad': '#3B82F6',
            'sport': '#10B981',
            'art': '#EC4899',
            'science': '#8B5CF6',
            'other': '#6B7280',
        }
        color = colors.get(obj.achievement_type, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 7px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_achievement_type_display()
        )
    achievement_type_badge.short_description = "Turi"

    def parent_consent_badge(self, obj):
        if obj.parent_consent:
            return format_html('<span style="color: #10B981; font-weight: bold;">✓ Mavjud</span>')
        return format_html('<span style="color: #EF4444; font-weight: bold;">✗ Yo\'q</span>')
    parent_consent_badge.short_description = "Rozilik"
