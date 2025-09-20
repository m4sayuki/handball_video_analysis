#!/bin/bash

echo "🐳 Docker インストール確認スクリプト"
echo "=================================="

# Dockerコマンドの存在確認
if command -v docker &> /dev/null; then
    echo "✅ Docker コマンドが見つかりました"
    
    # Dockerバージョン確認
    echo "📋 Docker バージョン:"
    docker --version
    
    # Docker Composeバージョン確認
    echo "📋 Docker Compose バージョン:"
    docker compose version
    
    # Dockerデーモンの動作確認
    echo "🔍 Docker デーモンの動作確認..."
    if docker info &> /dev/null; then
        echo "✅ Docker デーモンが正常に動作しています"
        echo ""
        echo "🎉 Docker のインストールが完了しました！"
        echo "以下のコマンドでアプリケーションを起動できます："
        echo "  docker compose up"
    else
        echo "❌ Docker デーモンが動作していません"
        echo "Docker Desktop を起動してください"
    fi
else
    echo "❌ Docker コマンドが見つかりません"
    echo "Docker Desktop をインストールしてください"
    echo "https://www.docker.com/products/docker-desktop/"
fi
