# AWS インフラ設定ガイド

ハンドボール動画解析プロジェクトで必要なAWSリソースの設定手順をまとめています。

## 📋 必要なAWSサービス

1. **Amazon S3** - 画像ファイルストレージ
2. **Amazon SQS** - プッシュ通知メッセージキュー
3. **Amazon EventBridge Scheduler** - プッシュ通知スケジューリング
4. **AWS IAM** - アクセス権限管理

---

## 🪣 1. Amazon S3 設定

### 1.1 S3バケットの作成

```bash
# AWS CLI での作成例
aws s3 mb s3://handball-video-analysis-bucket --region ap-northeast-1
```

**AWS コンソールでの作成手順:**
1. S3 コンソールにアクセス
2. 「バケットを作成」をクリック
3. バケット名: `handball-video-analysis-bucket`
4. リージョン: `アジアパシフィック (東京) ap-northeast-1`
5. パブリックアクセスをブロック: **有効のまま**
6. バケットポリシーで必要なアクセスのみ許可

### 1.2 バケット設定

**重要な設定:**
- ✅ **ACL無効**: 現在のプロジェクトはACL無効バケットに対応済み
- ✅ **バージョニング**: 任意（推奨は有効）
- ✅ **暗号化**: AES-256またはKMS

### 1.3 フォルダ構造

```
handball-video-analysis-bucket/
├── media/
│   └── push_notification_icons/  # プッシュ通知アイコン
└── test_uploads/                 # テスト用ファイル
```

---

## 🔄 2. Amazon SQS 設定

### 2.1 FIFO キューの作成

**AWS コンソールでの作成手順:**
1. SQS コンソールにアクセス
2. 「キューを作成」をクリック
3. **設定:**
   - タイプ: **FIFO**
   - 名前: `handball-push-notifications.fifo`
   - 可視性タイムアウト: `30秒`
   - メッセージ受信待機時間: `0秒`
   - メッセージ保持期間: `4日`
   - 最大メッセージサイズ: `256KB`
   - 配信遅延: `0秒`
   - 受信メッセージ数: `10`

### 2.2 FIFO 固有設定

- ✅ **コンテンツベース重複排除**: 有効
- ✅ **FIFOスループット制限**: 高スループット（推奨）
- ✅ **メッセージグループID**: 必須（アプリケーションで設定）

### 2.3 アクセスポリシー

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EventBridgeSchedulerAccess",
      "Effect": "Allow",
      "Principal": {
        "Service": "scheduler.amazonaws.com"
      },
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:ap-northeast-1:YOUR_ACCOUNT_ID:handball-push-notifications.fifo"
    }
  ]
}
```

---

## 📅 3. Amazon EventBridge Scheduler 設定

### 3.1 IAM サービスロールの作成

**信頼関係:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "scheduler.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**権限ポリシー:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage"
      ],
      "Resource": "arn:aws:sqs:ap-northeast-1:YOUR_ACCOUNT_ID:handball-push-notifications.fifo"
    }
  ]
}
```

### 3.2 ロール名
- 推奨名: `EventBridgeSchedulerRole`
- ARN例: `arn:aws:iam::YOUR_ACCOUNT_ID:role/EventBridgeSchedulerRole`

---

## 🔐 4. IAM ユーザー・権限設定

### 4.1 アプリケーション用IAMユーザー

**必要な権限:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::handball-video-analysis-bucket",
        "arn:aws:s3:::handball-video-analysis-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "scheduler:CreateSchedule",
        "scheduler:DeleteSchedule",
        "scheduler:GetSchedule",
        "scheduler:ListSchedules"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:PassRole"
      ],
      "Resource": "arn:aws:iam::YOUR_ACCOUNT_ID:role/EventBridgeSchedulerRole"
    }
  ]
}
```

### 4.2 アクセスキーの作成

1. IAM コンソール → ユーザー → セキュリティ認証情報
2. 「アクセスキーを作成」
3. **⚠️ シークレットキーは安全に保管**

---

## 🌍 5. リージョン設定

**推奨リージョン:** `ap-northeast-1` (東京)

**理由:**
- 日本国内でのレスポンス最適化
- データ主権の考慮
- 全サービスが利用可能

---

## 💰 6. コスト見積もり

### 6.1 月額概算（軽微な使用の場合）

| サービス | 使用量 | 月額コスト |
|----------|--------|------------|
| **S3** | 1GB ストレージ、1000リクエスト | ~$0.025 |
| **SQS** | 1000メッセージ | ~$0.0004 |
| **EventBridge Scheduler** | 100スケジュール | ~$0.01 |
| **合計** | | **~$0.04** |

### 6.2 コスト最適化

- ✅ S3 Intelligent-Tiering（大容量の場合）
- ✅ 不要なスケジュールの自動削除（実装済み）
- ✅ SQS メッセージの適切な処理

---

## 🔧 7. 環境変数設定

### 7.1 必要な環境変数

```env
# AWS 基本設定
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_S3_REGION_NAME=ap-northeast-1

# S3 設定
AWS_STORAGE_BUCKET_NAME=handball-video-analysis-bucket

# EventBridge Scheduler 設定
AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT_ID:role/EventBridgeSchedulerRole

# SQS 設定
AWS_SQS_QUEUE_ARN=arn:aws:sqs:ap-northeast-1:YOUR_ACCOUNT_ID:handball-push-notifications.fifo
AWS_SQS_MESSAGE_GROUP_ID=notice-push-notifications
```

### 7.2 YOUR_ACCOUNT_ID の確認方法

```bash
# AWS CLI で確認
aws sts get-caller-identity --query Account --output text
```

---

## ✅ 8. 設定確認手順

### 8.1 AWS CLI での確認

```bash
# S3バケット確認
aws s3 ls s3://handball-video-analysis-bucket

# SQSキュー確認
aws sqs list-queues --queue-name-prefix handball-push-notifications

# IAMロール確認
aws iam get-role --role-name EventBridgeSchedulerRole
```

### 8.2 アプリケーションでの確認

```bash
# 環境変数確認
python3 check_aws_env.py

# S3接続確認
python3 test_s3_simple.py

# EventBridge確認
python3 test_eventbridge_scheduler.py
```

---

## 🚨 9. セキュリティ考慮事項

### 9.1 アクセス制御

- ✅ **最小権限の原則**: 必要最小限の権限のみ付与
- ✅ **アクセスキーの定期ローテーション**
- ✅ **CloudTrail**: API呼び出しのログ記録（推奨）

### 9.2 データ保護

- ✅ **S3暗号化**: 保存時暗号化を有効
- ✅ **転送時暗号化**: HTTPS通信
- ✅ **バックアップ**: 重要データの定期バックアップ

### 9.3 監視・アラート

- ✅ **CloudWatch**: メトリクス監視
- ✅ **コスト異常検知**: 予期しない課金の早期発見
- ✅ **セキュリティアラート**: 不正アクセスの検知

---

## 📞 10. トラブルシューティング

### 10.1 よくあるエラー

| エラー | 原因 | 解決方法 |
|--------|------|----------|
| `NoCredentialsError` | 認証情報未設定 | 環境変数を確認 |
| `AccessDenied` | 権限不足 | IAMポリシーを確認 |
| `BucketNotFound` | バケット名間違い | バケット名・リージョンを確認 |
| `ResourceNotFoundException` | リソース未作成 | SQSキュー・IAMロールを確認 |

### 10.2 デバッグ手順

1. **環境変数確認**: `python3 check_aws_env.py`
2. **AWS CLI動作確認**: `aws sts get-caller-identity`
3. **個別サービステスト**: 各テストスクリプト実行
4. **CloudWatch Logs確認**: エラーログの詳細確認

---

## 🎯 次のステップ

1. ✅ AWSリソース作成
2. ✅ 環境変数設定
3. ✅ 接続テスト実行
4. ✅ 管理画面でのテスト
5. ✅ 本番環境デプロイ

このガイドに従って設定すれば、ハンドボール動画解析アプリケーションのAWS環境が完成します！