# Handball Video Analysis - Docker セットアップガイド

このガイドでは、Handball Video AnalysisアプリケーションをDockerで実行する方法を説明します。

## 前提条件

- Docker
- Docker Compose

## セットアップ手順

### 1. Docker Compose でアプリケーションを起動

```bash
# 全てのサービスを起動（初回起動時は.envファイルが自動作成されます）
docker compose up

# またはバックグラウンドで起動
docker compose up -d

# ログを確認
docker compose logs -f web
```

**注意**: 初回起動時、`.env`ファイルが存在しない場合は`env.docker`から自動的にコピーされます。

### 2. 環境変数のカスタマイズ（オプション）

AWS認証情報などをカスタマイズする場合は、起動後に`.env`ファイルを編集してください：

```bash
# .envファイルを編集
vim .env

# 変更後はコンテナを再起動
docker compose restart
```

### 3. スーパーユーザーの作成（オプション）

```bash
# コンテナ内でスーパーユーザーを作成
docker compose exec web python manage.py createsuperuser
```

または、環境変数で自動作成する場合は、`.env` ファイルに以下を追加：

```
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=your_secure_password
```

### 4. アプリケーションにアクセス

- **Webアプリケーション**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 基本的な使用方法

### 起動・停止

```bash
# 起動（フォアグラウンド）
docker compose up

# 起動（バックグラウンド）
docker compose up -d

# 停止
docker compose down

# 停止（ボリュームも削除）
docker compose down -v
```

## Docker Compose サービス

### web
- **説明**: Django Webアプリケーション
- **ポート**: 8000
- **依存関係**: db, redis

### db
- **説明**: PostgreSQL データベース
- **ポート**: 5432
- **認証情報**: 
  - ユーザー: postgres
  - パスワード: postgres
  - データベース: handball_video_analysis

### redis
- **説明**: Redis キャッシュサーバー
- **ポート**: 6379

## 開発時の使用方法

### コードの変更を反映

開発時はコードの変更が自動的に反映されます（ボリュームマウントにより）。

### データベースのマイグレーション

```bash
# マイグレーションファイルの作成
docker compose exec web python manage.py makemigrations

# マイグレーションの実行
docker compose exec web python manage.py migrate
```

### Django管理コマンドの実行

```bash
# Django shell
docker compose exec web python manage.py shell

# 静的ファイルの収集
docker compose exec web python manage.py collectstatic

# テストの実行
docker compose exec web python manage.py test
```

## 本番環境での使用

### 1. 環境変数の設定

本番環境では、以下の環境変数を適切に設定してください：

- `DEBUG=False`
- `SECRET_KEY`: 強力なシークレットキー
- `ALLOWED_HOSTS`: 適切なホスト名
- AWS認証情報（S3、EventBridge、SQS）

### 2. セキュリティ設定

- PostgreSQLのパスワードを変更
- Redisにパスワード認証を設定
- HTTPS設定
- ファイアウォール設定

### 3. データのバックアップ

```bash
# データベースのバックアップ
docker compose exec db pg_dump -U postgres handball_video_analysis > backup.sql

# データベースのリストア
docker compose exec -T db psql -U postgres handball_video_analysis < backup.sql
```

## トラブルシューティング

### コンテナの再起動

```bash
# 全サービスの再起動
docker compose restart

# 特定のサービスの再起動
docker compose restart web
```

### ログの確認

```bash
# 全サービスのログ
docker compose logs

# 特定のサービスのログ
docker compose logs web
docker compose logs db
```

### データベースの初期化

```bash
# 全データの削除（注意：データが失われます）
docker compose down -v
docker compose up -d
```

### ビルドの強制実行

```bash
# キャッシュを使わずにビルド
docker compose build --no-cache

# イメージの再構築と起動
docker compose up --build
```

## ファイル構成

- `Dockerfile`: Webアプリケーション用のDockerイメージ定義
- `docker-compose.yml`: 全サービスの構成定義
- `entrypoint.sh`: アプリケーション起動スクリプト
- `env.docker`: Docker用環境変数テンプレート
- `.dockerignore`: Dockerビルド時の除外ファイル定義

## 注意事項

- 開発環境では SQLite も使用可能です（`DATABASE_URL` を設定しない場合）
- AWS サービスを使用しない場合は、ローカルファイルストレージが使用されます
- Redis は オプションです（`REDIS_URL` を設定しない場合は使用されません）
