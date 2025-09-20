# Python 3.12のベースイメージを使用
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新と必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# entrypoint.shに実行権限を付与
RUN chmod +x /app/entrypoint.sh

# 静的ファイルを収集するためのディレクトリを作成
RUN mkdir -p /app/staticfiles

# メディアファイル用のディレクトリを作成
RUN mkdir -p /app/media

# ポート8000を公開
EXPOSE 8000

# 環境変数を設定
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=handball_video_analysis.settings

# エントリーポイントを設定
ENTRYPOINT ["/app/entrypoint.sh"]

# アプリケーションを起動
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
