from django.contrib import admin
from django.db import transaction
from django.contrib import messages
from .models import Notice
from .services import EventBridgeSchedulerService
import logging

logger = logging.getLogger(__name__)


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
    
    def save_model(self, request, obj, form, change):
        """
        モデル保存時の処理
        EventBridgeスケジュールの作成をトランザクションで管理
        """
        eventbridge_service = EventBridgeSchedulerService()
        
        # トランザクション開始
        with transaction.atomic():
            # データベースに保存
            super().save_model(request, obj, form, change)
            
            # プッシュ通知予定日時が設定されている場合、EventBridgeスケジュールを作成
            if obj.push_notification_scheduled_at:
                try:
                    success, error_message = eventbridge_service.create_push_notification_schedule(
                        obj.id, 
                        obj.push_notification_scheduled_at
                    )
                    
                    if success:
                        logger.info(f"EventBridgeスケジュールを作成しました (notice_id: {obj.id})")
                        messages.success(
                            request, 
                            f'お知らせを保存し、プッシュ通知スケジュール（{obj.push_notification_scheduled_at}）を作成しました。'
                        )
                    else:
                        # EventBridgeスケジュール作成に失敗した場合、トランザクションをロールバック
                        logger.error(f"EventBridgeスケジュール作成に失敗しました (notice_id: {obj.id}): {error_message}")
                        messages.error(
                            request, 
                            f'EventBridgeスケジュールの作成に失敗しました: {error_message}'
                        )
                        # トランザクションをロールバックするために例外を発生
                        raise Exception(f"EventBridgeスケジュール作成エラー: {error_message}")
                        
                except Exception as e:
                    logger.error(f"save_model でエラーが発生しました (notice_id: {obj.id}): {str(e)}")
                    messages.error(
                        request, 
                        f'保存処理中にエラーが発生しました: {str(e)}'
                    )
                    # 例外を再発生させてトランザクションをロールバック
                    raise
            else:
                # プッシュ通知予定日時が設定されていない場合は通常の保存
                messages.success(request, 'お知らせを保存しました。')
    
    def delete_model(self, request, obj):
        """
        モデル削除時の処理
        関連するEventBridgeスケジュールも削除
        """
        eventbridge_service = EventBridgeSchedulerService()
        
        # EventBridgeスケジュールを削除（エラーが発生しても削除処理は続行）
        try:
            success, error_message = eventbridge_service.delete_push_notification_schedule(obj.id)
            if success:
                logger.info(f"EventBridgeスケジュールを削除しました (notice_id: {obj.id})")
            else:
                logger.warning(f"EventBridgeスケジュール削除で警告 (notice_id: {obj.id}): {error_message}")
        except Exception as e:
            logger.error(f"EventBridgeスケジュール削除でエラー (notice_id: {obj.id}): {str(e)}")
        
        # データベースから削除
        super().delete_model(request, obj)
        messages.success(request, 'お知らせを削除しました。')
