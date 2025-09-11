# お知らせ管理画面バリデーション

このJavaScriptファイルは、お知らせ管理画面でのクライアントサイドバリデーション機能を提供します。

## 機能一覧

### 1. 画像拡張子のバリデーション
- プッシュ通知アイコン
- サムネイル画像
- 詳細画像

**デフォルト許可拡張子**: jpg, jpeg, png, gif, webp  
**エラー表示**: SweetAlert2でポップアップ表示  
**エラーメッセージ**: "{画像名}は{許可拡張子}以下の画像をアップロードしてください。"

### 2. 画像サイズのバリデーション
- プッシュ通知アイコン
- サムネイル画像
- 詳細画像

**デフォルト最大サイズ**: 5MB  
**エラー表示**: SweetAlert2でポップアップ表示  
**エラーメッセージ**: "{画像名}は{最大サイズ}以下の画像をアップロードしてください。"

### 3. 必須項目のバリデーション
- お知らせタイトル
- お知らせ区分
- ステータス
- 公開期間(from)

**エラーメッセージ**: "この項目は必須です。"

### 4. 公開期間の日付範囲バリデーション
プッシュ通知が有効な場合、公開期間(to)が公開期間(from)以降であることを確認します。

**エラーメッセージ**: "公開期間(to)は公開期間(from)以降の日付を指定してください。"

### 5. プッシュ通知予定日時のバリデーション
プッシュ通知が有効な場合、予定日時が現在時刻+5分以降であることを確認します。

**エラーメッセージ**: "プッシュ通知予定日時は現在時刻から5分以降の日時を指定してください。"

## SweetAlert2について

画像拡張子と画像サイズのバリデーションエラーは、SweetAlert2ライブラリを使用してポップアップで表示されます。

### 特徴
- 美しいモーダルポップアップでエラーを表示
- SweetAlert2が利用できない場合は通常のalert()にフォールバック
- エラーアイコンと分かりやすいメッセージ表示

### SweetAlertの設定
```javascript
Swal.fire({
    icon: 'error',
    title: 'エラータイトル',
    text: 'エラーメッセージ',
    confirmButtonText: 'OK',
    confirmButtonColor: '#d33'
});
```

## 設定のカスタマイズ

`notice_validation.js`ファイルの先頭にある`VALIDATION_CONFIG`オブジェクトを編集してください：

```javascript
const VALIDATION_CONFIG = {
    // 許可する画像拡張子
    ALLOWED_IMAGE_EXTENSIONS: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    // 最大画像サイズ（バイト単位）
    MAX_IMAGE_SIZE: 5 * 1024 * 1024, // 5MB
    // 最大画像サイズ表示用
    MAX_IMAGE_SIZE_DISPLAY: '5MB'
};
```

## 使用方法

### 自動初期化
DOMの読み込み完了後、自動的にバリデーション機能が初期化されます。

### 手動初期化
```javascript
// 手動で初期化する場合
initializeNoticeFormValidation();
```

### 個別バリデーション実行
```javascript
const validator = new NoticeFormValidator();
const formData = new FormData(document.querySelector('form'));
const formFields = {
    // フィールド要素を指定
};

const isValid = validator.validateAll(formData, formFields);
if (!isValid) {
    validator.displayErrors();
}
```

## プッシュ通知有効判定のカスタマイズ

`isPushNotificationEnabled`メソッドを、実際のフォーム構造に合わせて修正してください：

```javascript
isPushNotificationEnabled(formData) {
    // チェックボックスの場合
    const checkbox = document.querySelector('[name="push_notification_enabled"]');
    if (checkbox) {
        return checkbox.checked;
    }
    
    // 日時入力がある場合を有効と判定
    const scheduledAt = formData.get('push_notification_scheduled_at');
    return scheduledAt && scheduledAt.trim() !== '';
}
```

## エラー表示のカスタマイズ

CSSスタイルは管理画面テンプレートで定義されています：

```css
.field-error {
    color: #ba2121;
    font-size: 12px;
    margin-top: 5px;
    display: block;
}

.error {
    border-color: #ba2121 !important;
    background-color: #ffe6e6 !important;
}
```

## フィールド名のカスタマイズ

実際のフォームフィールド名に合わせて、以下の部分を修正してください：

```javascript
const formFields = {
    pushNotificationIcon: form.querySelector('[name="push_notification_icon"]'),
    listImageUrl: form.querySelector('[name="list_image_url"]'),
    detailImageUrl: form.querySelector('[name="detail_image_url"]'),
    // ... その他のフィールド
};
```

## トラブルシューティング

### バリデーションが動作しない場合
1. ブラウザの開発者ツールでJavaScriptエラーを確認
2. フォーム要素のセレクタが正しいか確認
3. DOMの読み込みタイミングを確認

### エラーメッセージが表示されない場合
1. CSSスタイルが正しく適用されているか確認
2. フィールド要素の親要素構造を確認

### カスタムバリデーションの追加
`NoticeFormValidator`クラスに新しいメソッドを追加し、`validateAll`メソッドから呼び出してください：

```javascript
validateCustomRule(formData) {
    // カスタムバリデーション処理
    if (/* 条件 */) {
        const field = document.querySelector('[name="field_name"]');
        this.addError(field, 'カスタムエラーメッセージ');
    }
}
```