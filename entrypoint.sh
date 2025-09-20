#!/bin/bash

# .envファイルが存在しない場合はenv.dockerからコピー
if [ ! -f /app/.env ]; then
    echo "📝 .envファイルが見つかりません。env.dockerからコピーします..."
    cp /app/env.docker /app/.env
    echo "✅ .envファイルを作成しました。"
fi

# データベースが利用可能になるまで待機
echo "⏳ データベースの起動を待機中..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "✅ データベースに接続しました"

# マイグレーションを実行
echo "🔄 データベースマイグレーションを実行中..."
python manage.py migrate --noinput

# 静的ファイルを収集
echo "📦 静的ファイルを収集中..."
python manage.py collectstatic --noinput

# スーパーユーザーを作成（環境変数が設定されている場合）
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 スーパーユーザーを作成中..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created.')
else:
    print('Superuser already exists.')
"
fi

# サーバーを起動
echo "🚀 Djangoサーバーを起動中..."
echo "🌐 アクセス先: http://localhost:8000"
exec "$@"
