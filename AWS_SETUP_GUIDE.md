# AWS S3 環境変数設定ガイド

このガイドでは、AWS S3を使用するための環境変数の設定方法を詳しく説明します。

## 必要な環境変数

以下の4つの環境変数が必要です：

| 環境変数名 | 説明 | 例 |
|-----------|------|-----|
| `AWS_ACCESS_KEY_ID` | AWSアクセスキーID | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWSシークレットアクセスキー | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_STORAGE_BUCKET_NAME` | S3バケット名 | `handball-video-analysis-bucket` |
| `AWS_S3_REGION_NAME` | AWSリージョン | `ap-northeast-1` |

## 1. 一時的な設定（セッション中のみ有効）

### macOS/Linux の場合

```bash
# ターミナルで以下のコマンドを実行
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
export AWS_STORAGE_BUCKET_NAME="your-bucket-name"
export AWS_S3_REGION_NAME="ap-northeast-1"
```

### Windows（Command Prompt）の場合

```cmd
set AWS_ACCESS_KEY_ID=your_access_key_id
set AWS_SECRET_ACCESS_KEY=your_secret_access_key
set AWS_STORAGE_BUCKET_NAME=your-bucket-name
set AWS_S3_REGION_NAME=ap-northeast-1
```

### Windows（PowerShell）の場合

```powershell
$env:AWS_ACCESS_KEY_ID="your_access_key_id"
$env:AWS_SECRET_ACCESS_KEY="your_secret_access_key"
$env:AWS_STORAGE_BUCKET_NAME="your-bucket-name"
$env:AWS_S3_REGION_NAME="ap-northeast-1"
```

## 2. 永続的な設定（ログイン時に自動読み込み）

### macOS/Linux - シェル設定ファイルに追加

使用しているシェルに応じて設定ファイルを編集します：

#### bashの場合（`~/.bashrc` または `~/.bash_profile`）

```bash
# ファイルを編集
nano ~/.bashrc

# 以下を追加
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
export AWS_STORAGE_BUCKET_NAME="your-bucket-name"
export AWS_S3_REGION_NAME="ap-northeast-1"

# 設定を反映
source ~/.bashrc
```

#### zshの場合（`~/.zshrc`）

```bash
# ファイルを編集
nano ~/.zshrc

# 以下を追加
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
export AWS_STORAGE_BUCKET_NAME="your-bucket-name"
export AWS_S3_REGION_NAME="ap-northeast-1"

# 設定を反映
source ~/.zshrc
```

### Windows - システム環境変数

1. **Windows + R** を押して「sysdm.cpl」を実行
2. **詳細設定** タブをクリック
3. **環境変数** ボタンをクリック
4. **システム環境変数** または **ユーザー環境変数** で **新規** をクリック
5. 各変数を追加：
   - 変数名: `AWS_ACCESS_KEY_ID`、値: `your_access_key_id`
   - 変数名: `AWS_SECRET_ACCESS_KEY`、値: `your_secret_access_key`
   - 変数名: `AWS_STORAGE_BUCKET_NAME`、値: `your-bucket-name`
   - 変数名: `AWS_S3_REGION_NAME`、値: `ap-northeast-1`

## 3. .envファイルを使用した設定（推奨）

プロジェクトルートに `.env` ファイルを作成して環境変数を管理する方法です。

### .envファイルの作成

```bash
# プロジェクトルートに.envファイルを作成
touch .env
```

### .envファイルの内容

```env
# AWS S3 Settings
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_STORAGE_BUCKET_NAME=handball-video-analysis-bucket
AWS_S3_REGION_NAME=ap-northeast-1
```

### python-dotenvの使用

```bash
# python-dotenvをインストール
pip install python-dotenv
```

## 4. AWS認証情報の取得方法

### AWS IAMでアクセスキーを作成

1. **AWS Management Console**にログイン
2. **IAM**サービスに移動
3. **ユーザー**を選択
4. 対象ユーザーをクリック
5. **セキュリティ認証情報**タブを選択
6. **アクセスキーを作成**をクリック
7. **アクセスキーID**と**シークレットアクセスキー**をメモ

### 必要な権限

S3バケットにアクセスするために、以下の権限が必要です：

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
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

## 5. 環境変数の確認方法

### 設定済み環境変数の確認

```bash
# すべての環境変数を表示
env

# AWS関連の環境変数のみを表示
env | grep AWS

# 特定の環境変数を表示
echo $AWS_ACCESS_KEY_ID
```

### Djangoプロジェクトでの確認

```python
import os
print("AWS_ACCESS_KEY_ID:", os.environ.get('AWS_ACCESS_KEY_ID'))
print("AWS_SECRET_ACCESS_KEY:", '***' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'Not set')
print("AWS_STORAGE_BUCKET_NAME:", os.environ.get('AWS_STORAGE_BUCKET_NAME'))
print("AWS_S3_REGION_NAME:", os.environ.get('AWS_S3_REGION_NAME'))
```

## 6. セキュリティ上の注意点

### ⚠️ 重要な注意事項

1. **シークレットアクセスキーは絶対に公開しない**
   - GitHubなどのバージョン管理システムにコミットしない
   - ログやエラーメッセージに出力しない

2. **.envファイルを.gitignoreに追加**
   ```
   # .gitignore
   .env
   *.env
   ```

3. **定期的なキーローテーション**
   - アクセスキーを定期的に更新する
   - 古いキーは無効化する

4. **最小権限の原則**
   - 必要最小限の権限のみを付与する

## 7. トラブルシューティング

### よくあるエラーと対処法

#### `NoCredentialsError: Unable to locate credentials`
- 環境変数が正しく設定されていない
- 変数名にスペルミスがある
- 仮想環境で設定していない

#### `AccessDenied` エラー
- IAMユーザーに適切な権限が付与されていない
- バケット名が間違っている

#### `BucketNotFound` エラー
- バケット名が間違っている
- バケットが存在しない
- リージョンが間違っている

### デバッグ用コマンド

```bash
# 環境変数の確認
python3 test_s3_simple.py

# Djangoコマンドでの詳細テスト
source path/to/venv/bin/activate && python manage.py test_s3_connection
```

## 8. 実際の設定例

### 開発環境での設定例

```bash
# ターミナルで実行
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_STORAGE_BUCKET_NAME="handball-video-analysis-dev"
export AWS_S3_REGION_NAME="ap-northeast-1"

# 設定確認
echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
echo "AWS_STORAGE_BUCKET_NAME: $AWS_STORAGE_BUCKET_NAME"

# S3接続テスト
python3 test_s3_simple.py
```

## 9. EventBridge Scheduler と SQS の設定

### EventBridge Scheduler 用 IAM ロールの作成

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

### IAM ロールに必要な権限

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage"
            ],
            "Resource": "arn:aws:sqs:ap-northeast-1:your-account-id:your-queue-name.fifo"
        }
    ]
}
```

### SQS FIFO キューの作成

1. **AWS SQS コンソール**にアクセス
2. **キューを作成**をクリック
3. **FIFO キュー**を選択
4. キュー名を入力（例：`handball-push-notifications.fifo`）
5. **メッセージグループID**を有効にする
6. **作成**をクリック

### 環境変数の追加設定

```env
# Amazon EventBridge Settings
AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN=arn:aws:iam::your-account-id:role/EventBridgeSchedulerRole

# Amazon SQS Settings
AWS_SQS_QUEUE_ARN=arn:aws:sqs:ap-northeast-1:your-account-id:your-queue-name.fifo
AWS_SQS_MESSAGE_GROUP_ID=notice-push-notifications
```

### EventBridge 機能のテスト

```bash
python3 test_eventbridge_scheduler.py
```

これで環境変数の設定は完了です！