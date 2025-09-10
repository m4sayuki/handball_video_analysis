#!/usr/bin/env python3
"""
簡単なS3接続テストスクリプト
Django環境を使わずに直接S3接続をテストします
"""

import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import sys


def test_s3_connection():
    """S3接続をテストする"""
    print("=== S3接続テスト ===")
    
    # 環境変数の確認
    print("\n1. 環境変数の確認...")
    required_vars = {
        'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_STORAGE_BUCKET_NAME': os.environ.get('AWS_STORAGE_BUCKET_NAME', 'handball-video-analysis-bucket'),
        'AWS_S3_REGION_NAME': os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-1')
    }
    
    for var_name, var_value in required_vars.items():
        if var_value:
            if 'SECRET' in var_name:
                display_value = '*' * len(var_value)
            else:
                display_value = var_value
            print(f"  ✓ {var_name}: {display_value}")
        else:
            print(f"  ⚠ {var_name}: 設定されていません")
    
    if not required_vars['AWS_ACCESS_KEY_ID'] or not required_vars['AWS_SECRET_ACCESS_KEY']:
        print("\n❌ AWS認証情報が設定されていません")
        print("以下のコマンドで環境変数を設定してください:")
        print("export AWS_ACCESS_KEY_ID=your_access_key")
        print("export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("export AWS_STORAGE_BUCKET_NAME=your_bucket_name")
        print("export AWS_S3_REGION_NAME=ap-northeast-1")
        return False
    
    # S3クライアントの作成
    print("\n2. S3クライアントの作成...")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=required_vars['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=required_vars['AWS_SECRET_ACCESS_KEY'],
            region_name=required_vars['AWS_S3_REGION_NAME']
        )
        print("  ✓ S3クライアントの作成に成功")
    except NoCredentialsError:
        print("  ❌ AWS認証情報が無効です")
        return False
    except Exception as e:
        print(f"  ❌ S3クライアントの作成に失敗: {e}")
        return False
    
    # バケットアクセステスト
    print("\n3. バケットアクセステスト...")
    bucket_name = required_vars['AWS_STORAGE_BUCKET_NAME']
    
    try:
        # バケットの存在確認
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"  ✓ バケット '{bucket_name}' にアクセス成功")
        
        # バケット内のオブジェクト一覧
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=3)
        if 'Contents' in response:
            print(f"  ✓ バケット内のファイル数: {len(response['Contents'])}件（最大3件表示）")
            for obj in response['Contents']:
                size_kb = obj['Size'] / 1024
                print(f"    - {obj['Key']} ({size_kb:.1f} KB)")
        else:
            print("  ✓ バケットは空です")
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"  ❌ バケット '{bucket_name}' が見つかりません")
        elif error_code == '403':
            print(f"  ❌ バケット '{bucket_name}' へのアクセス権限がありません")
        else:
            print(f"  ❌ バケットアクセスエラー: {e}")
        return False
    except Exception as e:
        print(f"  ❌ バケットアクセステストに失敗: {e}")
        return False
    
    print("\n✅ S3接続テスト成功！")
    return True


if __name__ == "__main__":
    success = test_s3_connection()
    sys.exit(0 if success else 1)