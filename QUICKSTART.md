# 🏐 Handball Video Analysis - クイックスタート

## 簡単起動手順

### 1. 起動
```bash
docker compose up
```

### 2. アクセス
- **Webアプリケーション**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

### 3. 停止
```bash
docker compose down
```

## 初回起動時の自動処理

✅ `.env`ファイルの自動作成（`env.docker`からコピー）  
✅ データベースのマイグレーション実行  
✅ 静的ファイルの収集  
✅ PostgreSQL、Redisの起動  

## よく使うコマンド

```bash
# バックグラウンド起動
docker compose up -d

# ログを見る
docker compose logs -f

# スーパーユーザー作成
docker compose exec web python manage.py createsuperuser

# Django shell
docker compose exec web python manage.py shell
```

## カスタマイズ

AWS設定などをカスタマイズする場合は、起動後に`.env`ファイルを編集してください：

```bash
# .envファイルを編集
vim .env

# 変更後は再起動
docker compose restart
```

---

詳細な設定方法は [`DOCKER_README.md`](DOCKER_README.md) をご覧ください。
