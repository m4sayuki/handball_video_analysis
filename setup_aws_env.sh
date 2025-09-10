#!/bin/bash

# AWS S3環境変数設定スクリプト
# Usage: source setup_aws_env.sh

echo "=== AWS S3 環境変数設定 ==="
echo

# 現在の設定を表示
echo "現在の設定:"
echo "AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:-未設定}"
echo "AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY:+設定済み}"
echo "AWS_STORAGE_BUCKET_NAME: ${AWS_STORAGE_BUCKET_NAME:-未設定}"
echo "AWS_S3_REGION_NAME: ${AWS_S3_REGION_NAME:-未設定}"
echo

# 対話的に環境変数を設定
read -p "AWS Access Key ID を入力してください: " AWS_ACCESS_KEY_ID
export AWS_ACCESS_KEY_ID

read -s -p "AWS Secret Access Key を入力してください: " AWS_SECRET_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY
echo

read -p "S3 バケット名を入力してください [handball-video-analysis-bucket]: " AWS_STORAGE_BUCKET_NAME
AWS_STORAGE_BUCKET_NAME=${AWS_STORAGE_BUCKET_NAME:-handball-video-analysis-bucket}
export AWS_STORAGE_BUCKET_NAME

read -p "AWS リージョンを入力してください [ap-northeast-1]: " AWS_S3_REGION_NAME
AWS_S3_REGION_NAME=${AWS_S3_REGION_NAME:-ap-northeast-1}
export AWS_S3_REGION_NAME

echo
echo "=== 設定完了 ==="
echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY: ***"
echo "AWS_STORAGE_BUCKET_NAME: $AWS_STORAGE_BUCKET_NAME"
echo "AWS_S3_REGION_NAME: $AWS_S3_REGION_NAME"
echo

# .envファイルの作成を提案
read -p ".envファイルに設定を保存しますか？ (y/n) [n]: " SAVE_TO_ENV
if [[ $SAVE_TO_ENV =~ ^[Yy]$ ]]; then
    cat > .env << EOF
# AWS S3 Settings
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME=$AWS_STORAGE_BUCKET_NAME
AWS_S3_REGION_NAME=$AWS_S3_REGION_NAME
EOF
    echo ".envファイルに設定を保存しました"
    
    # .gitignoreに.envを追加
    if [ ! -f .gitignore ] || ! grep -q "^\.env$" .gitignore; then
        echo ".env" >> .gitignore
        echo ".gitignoreに.envを追加しました"
    fi
fi

echo
echo "=== 接続テスト ==="
read -p "S3接続テストを実行しますか？ (y/n) [y]: " RUN_TEST
RUN_TEST=${RUN_TEST:-y}
if [[ $RUN_TEST =~ ^[Yy]$ ]]; then
    if [ -f "test_s3_simple.py" ]; then
        echo "簡単なS3接続テストを実行します..."
        python3 test_s3_simple.py
    else
        echo "test_s3_simple.py が見つかりません"
    fi
fi

echo
echo "設定が完了しました！"
echo "この設定は現在のシェルセッションでのみ有効です。"
echo "永続的に設定するには、~/.bashrc または ~/.zshrc に追加してください。"