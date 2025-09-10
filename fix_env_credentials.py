#!/usr/bin/env python3
"""
.env ファイルの認証情報修正支援スクリプト
"""

import os
from pathlib import Path

def main():
    """
    .envファイルの問題を診断し、修正方法を案内する
    """
    
    print("🔍 .env ファイルの認証情報を診断します...\n")
    
    env_file_path = Path(__file__).parent / '.env'
    
    if not env_file_path.exists():
        print("❌ .env ファイルが見つかりません")
        print("python3 create_env_file.py を実行して作成してください")
        return
    
    print("✅ .env ファイルが見つかりました")
    
    # .envファイルを読み込んで内容を確認
    with open(env_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 問題のある設定を特定
    problems = []
    
    if 'your_secret_access_key_here' in content:
        problems.append("AWS_SECRET_ACCESS_KEY がプレースホルダーのままです")
    
    if 'your_django_secret_key_here' in content:
        problems.append("SECRET_KEY がプレースホルダーのままです")
    
    if problems:
        print(f"\n❌ 以下の問題が見つかりました:")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. {problem}")
        
        print(f"\n🔧 修正方法:")
        print(f"1. テキストエディタで .env ファイルを開く:")
        print(f"   vi .env")
        print(f"   または")
        print(f"   code .env  # VS Code を使用している場合")
        
        print(f"\n2. 以下の値を実際の値に置き換える:")
        if 'your_secret_access_key_here' in content:
            print(f"   AWS_SECRET_ACCESS_KEY=your_secret_access_key_here")
            print(f"   ↓")
            print(f"   AWS_SECRET_ACCESS_KEY=実際のシークレットアクセスキー")
        
        if 'your_django_secret_key_here' in content:
            print(f"   SECRET_KEY=your_django_secret_key_here")
            print(f"   ↓") 
            print(f"   SECRET_KEY=実際のDjangoシークレットキー")
        
        print(f"\n💡 AWSシークレットアクセスキーの確認方法:")
        print(f"   - AWS Management Console → IAM → ユーザー → セキュリティ認証情報")
        print(f"   - または AWS CLI: aws configure list")
        
        print(f"\n💡 Djangoシークレットキーの生成:")
        print(f"   python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"")
        
    else:
        print("\n✅ .env ファイルの設定に問題は見つかりませんでした")
        
        # 実際にAWSアクセスをテスト
        print("\n🧪 AWS接続テスト:")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file_path)
            
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            sts_client = boto3.client('sts')
            response = sts_client.get_caller_identity()
            account_id = response['Account']
            
            print(f"   ✅ AWS接続成功")
            print(f"   ✅ アカウントID: {account_id}")
            print(f"   ✅ ユーザーARN: {response.get('Arn', 'N/A')}")
            
        except NoCredentialsError:
            print("   ❌ AWS認証情報が無効です")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'SignatureDoesNotMatch':
                print("   ❌ シークレットアクセスキーが正しくありません")
            else:
                print(f"   ❌ AWS API エラー: {e}")
        except Exception as e:
            print(f"   ❌ 予期しないエラー: {e}")
    
    print(f"\n📋 修正後の確認コマンド:")
    print(f"   python3 setup_eventbridge_role.py check")

if __name__ == "__main__":
    main()