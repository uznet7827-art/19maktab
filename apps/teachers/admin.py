from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Teacher


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ru', 'name_en')
    search_fields = ('name', 'name_ru', 'name_en')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'full_name', 'subject', 'position', 'department', 'experience_years', 'is_featured', 'is_active', 'order')
    list_filter = ('department', 'is_active', 'is_featured', 'experience_years')
    search_fields = ('full_name', 'subject', 'position', 'bio', 'education')
    list_editable = ('is_featured', 'is_active', 'order')

    fieldsets = (
        ("Shaxsiy ma'lumotlar", {
            'fields': (
                'full_name',
                'photo',
                'department',
                ('phone_email_group', 'email') if False else 'email',
            )
        }),
        ("Fani va lavozimi", {
            'fields': (
                ('subject', 'subject_ru', 'subject_en'),
                ('position', 'position_ru', 'position_en'),
                ('experience_years', 'education'),
            )
        }),
        ("Tarjimai hol", {
            'fields': (
                'bio',
                'bio_ru',
                'bio_en',
            )
        }),
        ("Sozlamalar", {
            'fields': (
                ('is_active', 'is_featured'),
                'order',
            )
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 50%;" />', obj.photo.url)
        return format_html('<span style="display:inline-block; width:45px; height:45px; background:#E5E7EB; border-radius:50%; text-align:center; line-height:45px; color:#9CA3AF;">👤</span>')
    thumbnail_preview.short_description = "Rasm"
