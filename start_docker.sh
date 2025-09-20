#!/bin/bash

echo "🏐 Handball Video Analysis - Docker起動スクリプト"
echo "================================================"

# .envファイルが存在しない場合はenv.dockerからコピー
if [ ! -f .env ]; then
    echo "📝 .envファイルが見つかりません。env.dockerからコピーします..."
    cp env.docker .env
    echo "✅ .envファイルを作成しました。必要に応じて編集してください。"
fi

echo "🚀 Docker Composeでアプリケーションを起動します..."

# Docker Composeでサービスを起動
docker-compose up -d

echo "⏳ サービスの起動を待機中..."
sleep 10

echo "📊 サービスの状態を確認中..."
docker-compose ps

echo ""
echo "🎉 起動完了！"
echo "=================================="
echo "🌐 Webアプリケーション: http://localhost:8000"
echo "🔧 Django Admin: http://localhost:8000/admin"
echo "🗄️  PostgreSQL: localhost:5432"
echo "🔄 Redis: localhost:6379"
echo "=================================="
echo ""
echo "📋 便利なコマンド:"
echo "  ログを見る: docker-compose logs -f"
echo "  停止する: docker-compose down"
echo "  再起動: docker-compose restart"
echo "  スーパーユーザー作成: docker-compose exec web python manage.py createsuperuser"
echo ""
