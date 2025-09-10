#!/usr/bin/env python3
"""
.envファイル作成支援スクリプト
"""

import os
from pathlib import Path

def create_env_file():
    """
    .envファイルを作成する
    ログから判明したAWSアカウントIDを使用
    """
    
    # ログから判明したAWSアカウントID
    aws_account_id = "413976100821"
    
    env_content = f"""# AWS S3 Settings
AWS_ACCESS_KEY_ID=AKIAWAYXF77KSHEY46YP
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here_replace_this
AWS_STORAGE_BUCKET_NAME=handball-video-analysis-bucket
AWS_S3_REGION_NAME=ap-northeast-1

# Amazon EventBridge Settings
AWS_EVENTBRIDGE_SCHEDULER_ROLE_ARN=arn:aws:iam::{aws_account_id}:role/EventBridgeSchedulerRole

# Amazon SQS Settings
AWS_SQS_QUEUE_ARN=arn:aws:sqs:ap-northeast-1:{aws_account_id}:handball-push-notifications.fifo
AWS_SQS_MESSAGE_GROUP_ID=notice-push-notifications

# Django Settings
DEBUG=True
SECRET_KEY=your_django_secret_key_here"""

    env_file_path = Path(__file__).parent / '.env'
    
    print(f"📝 .envファイルを作成します: {env_file_path}")
    
    try:
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ .envファイルを作成しました")
        print("\n⚠️  重要: 以下の値を実際の値に置き換えてください:")
        print("   - AWS_SECRET_ACCESS_KEY: 実際のシークレットアクセスキー")
        print("   - SECRET_KEY: Djangoのシークレットキー")
        print("\n🔧 次のステップ:")
        print("1. .envファイルを編集して実際の認証情報を設定")
        print("2. python3 setup_eventbridge_role.py check で確認")
        print("3. python3 setup_eventbridge_role.py create でIAMロール作成")
        
        return True
        
    except Exception as e:
        print(f"❌ .envファイルの作成に失敗: {e}")
        return False

if __name__ == "__main__":
    create_env_file()