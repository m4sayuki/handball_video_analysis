/**
 * お知らせ管理画面のバリデーション処理
 */

// 設定値（実際の値に置き換えてください）
const VALIDATION_CONFIG = {
    // 許可する画像拡張子
    ALLOWED_IMAGE_EXTENSIONS: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    // 最大画像サイズ（バイト単位）
    MAX_IMAGE_SIZE: 5 * 1024 * 1024, // 5MB
    // 最大画像サイズ表示用
    MAX_IMAGE_SIZE_DISPLAY: '5MB'
};

/**
 * お知らせフォームバリデーション
 */
class NoticeFormValidator {
    constructor() {
        this.errors = [];
    }

    /**
     * すべてのバリデーションを実行
     * @param {FormData} formData - フォームデータ
     * @param {Object} formFields - フォームフィールド要素
     * @returns {boolean} バリデーション結果
     */
    validateAll(formData, formFields) {
        this.errors = [];

        // ①画像拡張子のバリデーション
        this.validateImageExtensions(formFields);

        // ②画像サイズのバリデーション
        this.validateImageSizes(formFields);

        // ③必須項目のバリデーション
        this.validateRequiredFields(formData);

        // ④公開期間の日付範囲バリデーション
        this.validatePublishDateRange(formData);

        // ⑤プッシュ通知予定日時のバリデーション
        this.validatePushNotificationDateTime(formData);

        return this.errors.length === 0;
    }

    /**
     * ①画像拡張子のバリデーション
     * @param {Object} formFields - フォームフィールド要素
     */
    validateImageExtensions(formFields) {
        const imageFields = [
            { field: formFields.pushNotificationIcon, name: 'プッシュ通知アイコン' },
            { field: formFields.listImageUrl, name: 'サムネイル画像' },
            { field: formFields.detailImageUrl, name: '詳細画像' }
        ];

        imageFields.forEach(({ field, name }) => {
            if (field && field.files && field.files.length > 0) {
                const file = field.files[0];
                const extension = this.getFileExtension(file.name);
                
                if (!VALIDATION_CONFIG.ALLOWED_IMAGE_EXTENSIONS.includes(extension)) {
                    this.addSweetAlertError(
                        field,
                        '画像拡張子エラー',
                        `${name}は${VALIDATION_CONFIG.ALLOWED_IMAGE_EXTENSIONS.join(', ')}以下の画像をアップロードしてください。`
                    );
                }
            }
        });
    }

    /**
     * ②画像サイズのバリデーション
     * @param {Object} formFields - フォームフィールド要素
     */
    validateImageSizes(formFields) {
        const imageFields = [
            { field: formFields.pushNotificationIcon, name: 'プッシュ通知アイコン' },
            { field: formFields.listImageUrl, name: 'サムネイル画像' },
            { field: formFields.detailImageUrl, name: '詳細画像' }
        ];

        imageFields.forEach(({ field, name }) => {
            if (field && field.files && field.files.length > 0) {
                const file = field.files[0];
                
                if (file.size > VALIDATION_CONFIG.MAX_IMAGE_SIZE) {
                    this.addSweetAlertError(
                        field,
                        '画像サイズエラー',
                        `${name}は${VALIDATION_CONFIG.MAX_IMAGE_SIZE_DISPLAY}以下の画像をアップロードしてください。`
                    );
                }
            }
        });
    }

    /**
     * ③必須項目のバリデーション
     * @param {FormData} formData - フォームデータ
     */
    validateRequiredFields(formData) {
        const requiredFields = [
            { name: 'title', displayName: 'お知らせタイトル' },
            { name: 'notice_type', displayName: 'お知らせ区分' },
            { name: 'status', displayName: 'ステータス' },
            { name: 'publish_start_at', displayName: '公開期間(from)' }
        ];

        requiredFields.forEach(({ name, displayName }) => {
            const value = formData.get(name);
            if (!value || value.trim() === '') {
                const field = document.querySelector(`[name="${name}"]`);
                this.addError(field, 'この項目は必須です。');
            }
        });
    }

    /**
     * ④公開期間の日付範囲バリデーション
     * @param {FormData} formData - フォームデータ
     */
    validatePublishDateRange(formData) {
        const publishStartAt = formData.get('publish_start_at');
        const publishEndAt = formData.get('publish_end_at');

        // プッシュ通知する場合のみチェック
        const pushNotificationEnabled = this.isPushNotificationEnabled(formData);
        
        if (pushNotificationEnabled && publishStartAt && publishEndAt) {
            const startDate = new Date(publishStartAt);
            const endDate = new Date(publishEndAt);

            if (endDate < startDate) {
                const endField = document.querySelector('[name="publish_end_at"]');
                this.addError(endField, '公開期間(to)は公開期間(from)以降の日付を指定してください。');
            }
        }
    }

    /**
     * ⑤プッシュ通知予定日時のバリデーション
     * @param {FormData} formData - フォームデータ
     */
    validatePushNotificationDateTime(formData) {
        const pushNotificationEnabled = this.isPushNotificationEnabled(formData);
        
        if (pushNotificationEnabled) {
            const pushNotificationScheduledAt = formData.get('push_notification_scheduled_at');
            
            if (pushNotificationScheduledAt) {
                const scheduledDate = new Date(pushNotificationScheduledAt);
                const currentDate = new Date();
                const minimumDate = new Date(currentDate.getTime() + 5 * 60 * 1000); // 現在時刻 + 5分

                if (scheduledDate < minimumDate) {
                    const field = document.querySelector('[name="push_notification_scheduled_at"]');
                    this.addError(field, 'プッシュ通知予定日時は現在時刻から5分以降の日時を指定してください。');
                }
            }
        }
    }

    /**
     * プッシュ通知が有効かどうかを判定
     * @param {FormData} formData - フォームデータ
     * @returns {boolean} プッシュ通知有効フラグ
     */
    isPushNotificationEnabled(formData) {
        // 実際のフォーム構造に合わせて実装してください
        // 例：チェックボックスの場合
        const pushNotificationCheckbox = document.querySelector('[name="push_notification_enabled"]');
        if (pushNotificationCheckbox) {
            return pushNotificationCheckbox.checked;
        }
        
        // 例：プッシュ通知予定日時が設定されている場合
        const pushNotificationScheduledAt = formData.get('push_notification_scheduled_at');
        return pushNotificationScheduledAt && pushNotificationScheduledAt.trim() !== '';
    }

    /**
     * ファイル拡張子を取得
     * @param {string} filename - ファイル名
     * @returns {string} 拡張子（小文字）
     */
    getFileExtension(filename) {
        return filename.split('.').pop().toLowerCase();
    }

    /**
     * エラーを追加
     * @param {HTMLElement} field - フィールド要素
     * @param {string} message - エラーメッセージ
     */
    addError(field, message) {
        this.errors.push({
            field: field,
            message: message
        });
    }

    /**
     * エラーメッセージを表示
     */
    displayErrors() {
        // 既存のエラーメッセージをクリア
        this.clearErrors();

        this.errors.forEach(error => {
            this.showFieldError(error.field, error.message);
        });

        // 最初のエラーフィールドにフォーカス
        if (this.errors.length > 0 && this.errors[0].field) {
            this.errors[0].field.focus();
        }
    }

    /**
     * フィールドエラーを表示
     * @param {HTMLElement} field - フィールド要素
     * @param {string} message - エラーメッセージ
     */
    showFieldError(field, message) {
        if (!field) return;

        // エラークラスを追加
        field.classList.add('error');

        // エラーメッセージ要素を作成
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.textContent = message;
        errorElement.style.color = 'red';
        errorElement.style.fontSize = '12px';
        errorElement.style.marginTop = '5px';

        // フィールドの後にエラーメッセージを挿入
        if (field.parentNode) {
            field.parentNode.insertBefore(errorElement, field.nextSibling);
        }
    }

    /**
     * エラーメッセージをクリア
     */
    clearErrors() {
        // エラークラスを削除
        document.querySelectorAll('.error').forEach(element => {
            element.classList.remove('error');
        });

        // エラーメッセージ要素を削除
        document.querySelectorAll('.field-error').forEach(element => {
            element.remove();
        });
    }

    /**
     * エラー一覧を取得
     * @returns {Array} エラー配列
     */
    getErrors() {
        return this.errors;
    }
}

/**
 * フォーム送信時のバリデーション処理を初期化
 */
function initializeNoticeFormValidation() {
    const form = document.querySelector('#notice_form, form[name="notice_form"], .module form');
    if (!form) {
        console.warn('お知らせフォームが見つかりません');
        return;
    }

    const validator = new NoticeFormValidator();

    form.addEventListener('submit', function(event) {
        // フォームデータを取得
        const formData = new FormData(form);
        
        // フォームフィールドを取得
        const formFields = {
            pushNotificationIcon: form.querySelector('[name="push_notification_icon"]'),
            listImageUrl: form.querySelector('[name="list_image_url"]'),
            detailImageUrl: form.querySelector('[name="detail_image_url"]'),
            title: form.querySelector('[name="title"]'),
            noticeType: form.querySelector('[name="notice_type"]'),
            status: form.querySelector('[name="status"]'),
            publishStartAt: form.querySelector('[name="publish_start_at"]'),
            publishEndAt: form.querySelector('[name="publish_end_at"]'),
            pushNotificationScheduledAt: form.querySelector('[name="push_notification_scheduled_at"]')
        };

        // バリデーション実行
        const isValid = validator.validateAll(formData, formFields);

        if (!isValid) {
            // エラーがある場合は送信を停止
            event.preventDefault();
            
            // エラーメッセージを表示
            validator.displayErrors();
            
            // アラートでエラー通知（オプション）
            // alert('入力内容にエラーがあります。確認してください。');
        }
    });

    // リアルタイムバリデーション（オプション）
    const fieldsToWatch = [
        'push_notification_icon',
        'list_image_url', 
        'detail_image_url',
        'title',
        'notice_type',
        'status',
        'publish_start_at',
        'publish_end_at',
        'push_notification_scheduled_at'
    ];

    fieldsToWatch.forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.addEventListener('change', function() {
                // 個別フィールドの既存エラーをクリア
                this.classList.remove('error');
                const errorElement = this.parentNode.querySelector('.field-error');
                if (errorElement) {
                    errorElement.remove();
                }
            });
        }
    });
}

// DOM読み込み完了後に初期化
document.addEventListener('DOMContentLoaded', initializeNoticeFormValidation);

// 外部からアクセス可能にする
window.NoticeFormValidator = NoticeFormValidator;
window.initializeNoticeFormValidation = initializeNoticeFormValidation;