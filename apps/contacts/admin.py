from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.http import FileResponse
import os

from .models import Contact
from .excel_service import export_all_contacts_to_excel, sync_contact_to_excel


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'contact_type_badge', 'subject', 'phone', 'email', 'status_badge', 'created_at')
    list_filter = ('status', 'contact_type', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'subject', 'message', 'admin_reply')
    readonly_fields = ('ip_address', 'created_at', 'replied_at')
    actions = ['mark_as_read', 'mark_as_closed', 'export_to_excel']

    fieldsets = (
        ("Murojaatchi ma'lumotlari", {
            'fields': (
                'full_name',
                ('phone', 'email'),
                'contact_type',
                'privacy_agreed',
                'ip_address',
                'created_at',
            )
        }),
        ("Murojaat matni", {
            'fields': (
                'subject',
                'message',
            )
        }),
        ("Administrator javobi va holati", {
            'fields': (
                'status',
                'admin_reply',
                'replied_at',
            )
        }),
    )

    def contact_type_badge(self, obj):
        colors = {
            'general': '#3B82F6',
            'admission': '#10B981',
            'complaint': '#EF4444',
            'suggestion': '#8B5CF6',
            'other': '#6B7280',
        }
        color = colors.get(obj.contact_type, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 7px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_contact_type_display()
        )
    contact_type_badge.short_description = "Turi"

    def status_badge(self, obj):
        colors = {
            'new': '#EF4444',
            'read': '#F59E0B',
            'replied': '#10B981',
            'closed': '#6B7280',
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 7px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Holat"

    @admin.action(description="O'qilgan deb belgilash")
    def mark_as_read(self, request, queryset):
        queryset.update(status='read')

    @admin.action(description="Tanlangan murojaatlarni Excel (.xlsx) ga yuklab olish")
    def export_to_excel(self, request, queryset):
        excel_path = export_all_contacts_to_excel(queryset=queryset)
        filename = f"murojaatlar-{timezone.now().strftime('%Y-%m-%d')}.xlsx"
        return FileResponse(
            open(excel_path, 'rb'),
            as_attachment=True,
            filename=filename,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def save_model(self, request, obj, form, change):
        if obj.admin_reply and not obj.replied_at:
            obj.replied_at = timezone.now()
            if obj.status == 'new' or obj.status == 'read':
                obj.status = 'replied'
        super().save_model(request, obj, form, change)
        sync_contact_to_excel(obj)
