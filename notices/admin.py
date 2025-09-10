from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """お知らせ管理画面"""
    
    list_display = [
        'id', 'title', 'notice_type', 'status', 
        'publish_start_at', 'publish_end_at', 'created_at'
    ]
    list_filter = [
        'notice_type', 'status', 'created_at', 'publish_start_at'
    ]
    search_fields = ['title', 'short_description', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('id', 'title', 'notice_type', 'status')
        }),
        ('公開設定', {
            'fields': ('publish_start_at', 'publish_end_at')
        }),
        ('プッシュ通知', {
            'fields': ('push_notification_scheduled_at', 'push_notification_icon'),
            'classes': ('collapse',)
        }),
        ('画像・URL', {
            'fields': ('list_image_url', 'detail_image_url', 'redirect_url'),
            'classes': ('collapse',)
        }),
        ('本文', {
            'fields': ('short_description', 'description')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    list_per_page = 20
