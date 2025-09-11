from django.db import models


class Notice(models.Model):
    """お知らせモデル"""
    
    # お知らせ区分の選択肢
    NOTICE_TYPE_CHOICES = [
        (1, '重要'),
        (2, '一般'),
        (3, 'イベント'),
        (4, 'メンテナンス'),
    ]
    
    # ステータスの選択肢
    STATUS_CHOICES = [
        (1, '下書き'),
        (2, '公開中'),
        (3, '非公開'),
        (4, '削除'),
    ]
    
    # 基本フィールド
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    title = models.CharField('タイトル', max_length=300)
    notice_type = models.SmallIntegerField('お知らせ区分', choices=NOTICE_TYPE_CHOICES)
    publish_start_at = models.DateTimeField('公開開始日時', null=True, blank=True)
    publish_end_at = models.DateTimeField('公開終了日時', null=True, blank=True)
    status = models.SmallIntegerField('ステータス', choices=STATUS_CHOICES, default=1)
    
    # プッシュ通知関連
    push_notification_scheduled_at = models.DateTimeField('プッシュ通知予定日時', null=True, blank=True)
    push_notification_icon_url = models.URLField(
        'プッシュ通知アイコンURL', 
        max_length=2048,
        null=True, 
        blank=True,
        help_text='推奨サイズ: 512x512px。アップロードはサービスクラス経由で行います。'
    )
    
    # 画像URL
    list_image_url = models.URLField('一覧画像URL', max_length=2048, blank=True)
    detail_image_url = models.URLField('詳細画像URL', max_length=2048, blank=True)
    
    # 本文
    short_description = models.CharField('簡易版本文', max_length=1000, blank=True)
    description = models.TextField('本文', blank=True)
    
    # 遷移先
    redirect_url = models.URLField('遷移先URL', max_length=2048, blank=True)
    
    class Meta:
        db_table = 'notices'
        verbose_name = 'お知らせ'
        verbose_name_plural = 'お知らせ'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
