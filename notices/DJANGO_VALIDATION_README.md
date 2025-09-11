# Django サーバーサイドバリデーション

このドキュメントでは、お知らせ管理画面で実装されたDjangoのサーバーサイドバリデーション機能について説明します。

## 実装されたバリデーション

### ①日付フォーマットのバリデーション

以下の項目で日付フォーマットが正しいことを確認します：

- **公開期間(from)** - `publish_start_at`
- **公開期間(to)** - `publish_end_at`（nullの場合を除く）
- **プッシュ通知予定日時** - `push_notification_scheduled_at`（空文字の場合を除く）

**実装方法:**
```python
class DateTimeLocalWidget(forms.DateTimeInput):
    """HTML5のdatetime-localタイプを使用するカスタムウィジェット"""
    input_type = 'datetime-local'
```

**特徴:**
- HTML5の`datetime-local`タイプを使用
- ブラウザネイティブの日付・時刻ピッカーを提供
- 自動的に正しい形式（YYYY-MM-DDTHH:MM）を強制

### ②日付範囲のバリデーション

**公開期間の範囲チェック:**
```python
def _validate_publish_date_range(self, cleaned_data):
    publish_start_at = cleaned_data.get('publish_start_at')
    publish_end_at = cleaned_data.get('publish_end_at')
    
    if publish_start_at and publish_end_at:
        if publish_end_at < publish_start_at:
            raise ValidationError({
                'publish_end_at': '公開期間(to)は公開期間(from)以降の日付を指定してください。'
            })
```

**プッシュ通知予定日時のチェック:**
```python
def _validate_push_notification_datetime(self, cleaned_data):
    push_notification_scheduled_at = cleaned_data.get('push_notification_scheduled_at')
    
    if push_notification_scheduled_at:
        current_time = timezone.now()
        minimum_time = current_time + timedelta(minutes=5)
        
        if push_notification_scheduled_at < minimum_time:
            raise ValidationError({
                'push_notification_scheduled_at': 'プッシュ通知予定日時は現在時刻から5分以降の日時を指定してください。'
            })
```

### ③画像拡張子のバリデーション

**対象フィールド:**
- プッシュ通知アイコン
- サムネイル画像（ファイルフィールドの場合）
- 詳細画像（ファイルフィールドの場合）

**許可拡張子:** jpg, jpeg, png, gif, webp

**実装:**
```python
def _validate_image_extension(self, image_file, field_name):
    if not image_file:
        return
    
    file_extension = os.path.splitext(image_file.name)[1].lower().lstrip('.')
    
    if file_extension not in self.ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'{field_name}は{", ".join(self.ALLOWED_IMAGE_EXTENSIONS)}の拡張子の画像をアップロードしてください。'
        )
```

### ④画像サイズのバリデーション

**最大サイズ:** 5MB

**実装:**
```python
def _validate_image_size(self, image_file, field_name):
    if not image_file:
        return
    
    if image_file.size > self.MAX_IMAGE_SIZE:
        raise ValidationError(
            f'{field_name}は{self.MAX_IMAGE_SIZE_DISPLAY}以下の画像をアップロードしてください。'
        )
```

## ファイル構成

### `notices/forms.py`
- `NoticeAdminForm` - メインのバリデーションフォーム
- `DateTimeLocalWidget` - 日付時刻入力用カスタムウィジェット
- `NoticeImageUploadForm` - 画像アップロード専用フォーム（必要に応じて使用）

### `notices/admin.py`
```python
from .forms import NoticeAdminForm

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    form = NoticeAdminForm  # カスタムフォームを指定
```

### `requirements.txt`
```
Django>=5.2
django-storages>=1.14
boto3>=1.34
python-dotenv>=1.0
Pillow>=10.0.0  # 画像処理に必要
```

## 使用方法

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. マイグレーション実行
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. 管理画面での動作確認
- Django管理画面にアクセス
- お知らせの新規作成・編集画面で各バリデーションが動作することを確認

## カスタマイズ

### バリデーション設定の変更

`notices/forms.py`の`NoticeAdminForm`クラス内の設定を変更：

```python
class NoticeAdminForm(forms.ModelForm):
    # バリデーション設定
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_SIZE_DISPLAY = '5MB'
```

### 新しいバリデーションの追加

1. **単一フィールドのバリデーション:**
```python
def clean_fieldname(self):
    value = self.cleaned_data.get('fieldname')
    
    # バリデーション処理
    if not_valid_condition:
        raise ValidationError('エラーメッセージ')
    
    return value
```

2. **複数フィールドのバリデーション:**
```python
def clean(self):
    cleaned_data = super().clean()
    
    # 複数フィールドにまたがるバリデーション
    self._custom_validation_method(cleaned_data)
    
    return cleaned_data
```

### ウィジェットのカスタマイズ

```python
class Meta:
    model = Notice
    fields = '__all__'
    widgets = {
        'field_name': CustomWidget(attrs={
            'class': 'custom-class',
            'placeholder': 'プレースホルダー'
        }),
    }
```

## エラーハンドリング

### バリデーションエラーの種類

1. **フィールドレベルエラー** - 特定のフィールドに関連
2. **フォームレベルエラー** - 複数フィールドにまたがるエラー

### エラーメッセージの表示

- Django管理画面で自動的にエラーメッセージが表示される
- フィールドごとにエラー内容が表示される
- 日本語でユーザーフレンドリーなメッセージ

## 注意事項

### URLフィールドの制限

現在のモデルで`list_image_url`と`detail_image_url`がURLFieldの場合：
- 実際のファイルアップロードではないため、拡張子・サイズチェックは困難
- 必要に応じてImageFieldに変更することを推奨

### タイムゾーンの考慮

プッシュ通知予定日時のバリデーションでは、`timezone.now()`を使用してタイムゾーンを適切に処理しています。

### 画像処理の依存関係

Pillowライブラリを使用して画像の整合性チェックを行っています。インストールが必要です。

## トラブルシューティング

### Pillowのインストールエラー
```bash
# macOS
brew install libjpeg libpng

# Ubuntu/Debian
sudo apt-get install libjpeg-dev libpng-dev

pip install Pillow
```

### 日付フォーマットエラー
- ブラウザがHTML5のdatetime-localをサポートしているか確認
- 必要に応じて追加のJavaScriptライブラリを使用

### バリデーションが動作しない
1. `form = NoticeAdminForm`がadmin.pyで設定されているか確認
2. フォームのclean_*メソッドが正しく定義されているか確認
3. Django管理画面でエラーメッセージが表示されているか確認