from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
import os
from PIL import Image
from .models import Notice
from .services import S3FileUploadService


class DateTimeLocalWidget(forms.DateTimeInput):
    """HTML5のdatetime-localタイプを使用するカスタムウィジェット"""
    input_type = 'datetime-local'
    
    def format_value(self, value):
        if value:
            # datetime-local形式に変換 (YYYY-MM-DDTHH:MM)
            if isinstance(value, datetime):
                return value.strftime('%Y-%m-%dT%H:%M')
            elif isinstance(value, str):
                # 文字列の場合はそのまま返す
                return value
        return ''
    
    def value_from_datadict(self, data, files, name):
        """フォームからの値を適切に処理"""
        value = data.get(name)
        if value:
            # datetime-local形式の値を適切に処理
            if isinstance(value, str) and 'T' in value:
                # ISO 8601形式をDjangoが理解できる形式に変換
                try:
                    # datetime-local形式 (YYYY-MM-DDTHH:MM) を処理
                    return value.replace('T', ' ')
                except Exception:
                    pass
            return value
        return None


class NoticeAdminForm(forms.ModelForm):
    """お知らせ管理画面用のカスタムフォーム"""
    
    # バリデーション設定
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_SIZE_DISPLAY = '5MB'
    
    # プッシュ通知アイコンアップロード用のフィールド（実際のモデルフィールドではない）
    push_notification_icon_file = forms.ImageField(
        label='プッシュ通知アイコン（アップロード）',
        required=False,
        help_text='推奨サイズ: 512x512px。アップロードするとURLフィールドに自動設定されます。'
    )
    
    # 明示的なフィールド定義
    publish_start_at = forms.DateTimeField(
        label='公開開始日時',
        required=False,
        widget=DateTimeLocalWidget(attrs={
            'class': 'datetime-input',
            'step': '60'
        }),
        help_text='公開開始日時を選択してください'
    )
    
    publish_end_at = forms.DateTimeField(
        label='公開終了日時',
        required=False,
        widget=DateTimeLocalWidget(attrs={
            'class': 'datetime-input',
            'step': '60'
        }),
        help_text='公開終了日時を選択してください'
    )
    
    push_notification_scheduled_at = forms.DateTimeField(
        label='プッシュ通知予定日時',
        required=False,
        widget=DateTimeLocalWidget(attrs={
            'class': 'datetime-input',
            'step': '60'
        }),
        help_text='プッシュ通知の送信日時を選択してください'
    )
    
    class Meta:
        model = Notice
        fields = '__all__'
    
    def clean_publish_start_at(self):
        """①公開期間(from)の日付フォーマットバリデーション"""
        publish_start_at = self.cleaned_data.get('publish_start_at')
        
        if publish_start_at:
            # 文字列の場合は datetime オブジェクトに変換
            if isinstance(publish_start_at, str):
                try:
                    from django.utils.dateparse import parse_datetime
                    parsed_datetime = parse_datetime(publish_start_at)
                    if parsed_datetime:
                        publish_start_at = parsed_datetime
                    else:
                        raise ValidationError('正しい日時形式で入力してください。')
                except ValueError:
                    raise ValidationError('正しい日時形式で入力してください。')
        
        return publish_start_at
    
    def clean_publish_end_at(self):
        """①公開期間(to)の日付フォーマットバリデーション"""
        publish_end_at = self.cleaned_data.get('publish_end_at')
        
        if publish_end_at:
            # 文字列の場合は datetime オブジェクトに変換
            if isinstance(publish_end_at, str):
                try:
                    from django.utils.dateparse import parse_datetime
                    parsed_datetime = parse_datetime(publish_end_at)
                    if parsed_datetime:
                        publish_end_at = parsed_datetime
                    else:
                        raise ValidationError('正しい日時形式で入力してください。')
                except ValueError:
                    raise ValidationError('正しい日時形式で入力してください。')
        
        return publish_end_at
    
    def clean_push_notification_scheduled_at(self):
        """①プッシュ通知予定日時の日付フォーマットバリデーション"""
        push_notification_scheduled_at = self.cleaned_data.get('push_notification_scheduled_at')
        
        if push_notification_scheduled_at:
            # 文字列の場合は datetime オブジェクトに変換
            if isinstance(push_notification_scheduled_at, str):
                try:
                    from django.utils.dateparse import parse_datetime
                    parsed_datetime = parse_datetime(push_notification_scheduled_at)
                    if parsed_datetime:
                        push_notification_scheduled_at = parsed_datetime
                    else:
                        raise ValidationError('正しい日時形式で入力してください。')
                except ValueError:
                    raise ValidationError('正しい日時形式で入力してください。')
        
        return push_notification_scheduled_at
    
    def clean_push_notification_icon_file(self):
        """③④プッシュ通知アイコンファイルの拡張子とサイズバリデーション"""
        icon = self.cleaned_data.get('push_notification_icon_file')
        
        if icon:
            # 拡張子チェック
            self._validate_image_extension(icon, 'プッシュ通知アイコン')
            
            # サイズチェック
            self._validate_image_size(icon, 'プッシュ通知アイコン')
            
            # 画像形式チェック（追加の安全性確保）
            self._validate_image_format(icon, 'プッシュ通知アイコン')
        
        return icon
    
    def clean_list_image_url(self):
        """サムネイル画像のバリデーション（URLフィールドの場合）"""
        # URLフィールドの場合は、実際のファイルアップロードではないため
        # 拡張子やサイズのチェックは困難
        # 必要に応じてURL形式のバリデーションを追加
        list_image_url = self.cleaned_data.get('list_image_url')
        return list_image_url
    
    def clean_detail_image_url(self):
        """詳細画像のバリデーション（URLフィールドの場合）"""
        # URLフィールドの場合は、実際のファイルアップロードではないため
        # 拡張子やサイズのチェックは困難
        # 必要に応じてURL形式のバリデーションを追加
        detail_image_url = self.cleaned_data.get('detail_image_url')
        return detail_image_url
    
    def clean(self):
        """②複数フィールドにまたがるバリデーション"""
        cleaned_data = super().clean()
        
        # 公開期間の範囲チェック
        self._validate_publish_date_range(cleaned_data)
        
        # プッシュ通知予定日時のチェック
        self._validate_push_notification_datetime(cleaned_data)
        
        return cleaned_data
    
    def save(self, commit=True):
        """カスタム保存処理でS3アップロードサービスを使用"""
        instance = super().save(commit=False)
        
        # プッシュ通知アイコンファイルがアップロードされた場合の処理
        icon_file = self.cleaned_data.get('push_notification_icon_file')
        if icon_file:
            s3_service = S3FileUploadService()
            success, result = s3_service.upload_push_notification_icon(icon_file)
            
            if success:
                instance.push_notification_icon_url = result
            else:
                raise ValidationError(f'プッシュ通知アイコンのアップロードに失敗しました: {result}')
        
        if commit:
            instance.save()
        
        return instance
    
    def _validate_image_extension(self, image_file, field_name):
        """画像拡張子のバリデーション"""
        if not image_file:
            return
        
        # ファイル名から拡張子を取得
        file_extension = os.path.splitext(image_file.name)[1].lower().lstrip('.')
        
        if file_extension not in self.ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(
                f'{field_name}は{", ".join(self.ALLOWED_IMAGE_EXTENSIONS)}の拡張子の画像をアップロードしてください。'
            )
    
    def _validate_image_size(self, image_file, field_name):
        """画像サイズのバリデーション"""
        if not image_file:
            return
        
        if image_file.size > self.MAX_IMAGE_SIZE:
            raise ValidationError(
                f'{field_name}は{self.MAX_IMAGE_SIZE_DISPLAY}以下の画像をアップロードしてください。'
            )
    
    def _validate_image_format(self, image_file, field_name):
        """画像形式の追加バリデーション（PILを使用）"""
        if not image_file:
            return
        
        try:
            # PILで画像を開いて形式を確認
            image = Image.open(image_file)
            image.verify()  # 画像の整合性をチェック
            
            # ファイルポインタをリセット
            image_file.seek(0)
            
        except Exception as e:
            raise ValidationError(
                f'{field_name}は有効な画像ファイルをアップロードしてください。'
            )
    
    def _validate_publish_date_range(self, cleaned_data):
        """②公開期間の範囲バリデーション"""
        publish_start_at = cleaned_data.get('publish_start_at')
        publish_end_at = cleaned_data.get('publish_end_at')
        
        if publish_start_at and publish_end_at:
            if publish_end_at < publish_start_at:
                raise ValidationError({
                    'publish_end_at': '公開期間(to)は公開期間(from)以降の日付を指定してください。'
                })
    
    def _validate_push_notification_datetime(self, cleaned_data):
        """②プッシュ通知予定日時のバリデーション"""
        push_notification_scheduled_at = cleaned_data.get('push_notification_scheduled_at')
        
        # プッシュ通知が設定されている場合のみチェック
        if push_notification_scheduled_at:
            current_time = timezone.now()
            minimum_time = current_time + timedelta(minutes=5)
            
            # タイムゾーンを考慮した比較
            if push_notification_scheduled_at < minimum_time:
                raise ValidationError({
                    'push_notification_scheduled_at': 'プッシュ通知予定日時は現在時刻から5分以降の日時を指定してください。'
                })


class NoticeImageUploadForm(forms.ModelForm):
    """画像アップロード専用フォーム（サムネイル画像、詳細画像がファイルフィールドの場合）"""
    
    # 実際のモデルに合わせてフィールドを調整してください
    thumbnail_image = forms.ImageField(
        label='サムネイル画像',
        required=False,
        help_text='推奨サイズ: 300x200px'
    )
    detail_image = forms.ImageField(
        label='詳細画像', 
        required=False,
        help_text='推奨サイズ: 800x600px'
    )
    
    class Meta:
        model = Notice
        fields = ['thumbnail_image', 'detail_image']  # 実際のフィールド名に合わせて調整
    
    def clean_thumbnail_image(self):
        """サムネイル画像のバリデーション"""
        image = self.cleaned_data.get('thumbnail_image')
        
        if image:
            form = NoticeAdminForm()
            form._validate_image_extension(image, 'サムネイル画像')
            form._validate_image_size(image, 'サムネイル画像')
            form._validate_image_format(image, 'サムネイル画像')
        
        return image
    
    def clean_detail_image(self):
        """詳細画像のバリデーション"""
        image = self.cleaned_data.get('detail_image')
        
        if image:
            form = NoticeAdminForm()
            form._validate_image_extension(image, '詳細画像')
            form._validate_image_size(image, '詳細画像')
            form._validate_image_format(image, '詳細画像')
        
        return image