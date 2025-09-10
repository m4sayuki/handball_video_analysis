#!/usr/bin/env python3
"""
S3バケットの内容を詳しく確認するスクリプト
"""

import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import sys
from datetime import datetime


def load_env_file(env_path='.env'):
    """
    .envファイルを読み込んで環境変数に設定する
    """
    if not os.path.exists(env_path):
        print(f"⚠️  {env_path} ファイルが見つかりません")
        return False
    
    try:
        with open(env_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    if key not in os.environ:
                        os.environ[key] = value
        
        return True
        
    except Exception as e:
        print(f"❌ {env_path} ファイルの読み込みに失敗: {e}")
        return False


def get_s3_client():
    """
    S3クライアントを取得
    """
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region_name = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-1')
    
    if not aws_access_key_id or not aws_secret_access_key:
        print("❌ AWS認証情報が設定されていません")
        return None
    
    try:
        return boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
    except Exception as e:
        print(f"❌ S3クライアントの作成に失敗: {e}")
        return None


def list_all_objects(s3_client, bucket_name):
    """
    バケット内のすべてのオブジェクトを一覧表示
    """
    print(f"📂 バケット '{bucket_name}' の全内容:")
    
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)
        
        total_objects = 0
        total_size = 0
        folders = {}
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    total_objects += 1
                    total_size += obj['Size']
                    
                    # フォルダ別に分類
                    key = obj['Key']
                    if '/' in key:
                        folder = key.split('/')[0]
                        if folder not in folders:
                            folders[folder] = {'count': 0, 'size': 0, 'files': []}
                        folders[folder]['count'] += 1
                        folders[folder]['size'] += obj['Size']
                        folders[folder]['files'].append({
                            'key': key,
                            'size': obj['Size'],
                            'modified': obj['LastModified']
                        })
                    else:
                        # ルートレベルのファイル
                        if 'root' not in folders:
                            folders['root'] = {'count': 0, 'size': 0, 'files': []}
                        folders['root']['count'] += 1
                        folders['root']['size'] += obj['Size']
                        folders['root']['files'].append({
                            'key': key,
                            'size': obj['Size'],
                            'modified': obj['LastModified']
                        })
        
        if total_objects == 0:
            print("   バケットは空です")
            return
        
        print(f"   総オブジェクト数: {total_objects:,}")
        print(f"   総サイズ: {total_size / 1024 / 1024:.2f} MB")
        print()
        
        # フォルダ別の詳細を表示
        for folder_name, folder_info in folders.items():
            if folder_name == 'root':
                print("📁 ルートレベル:")
            else:
                print(f"📁 {folder_name}/:")
            
            print(f"   ファイル数: {folder_info['count']}")
            print(f"   合計サイズ: {folder_info['size'] / 1024:.1f} KB")
            
            # 最新の5ファイルを表示
            recent_files = sorted(folder_info['files'], 
                                key=lambda x: x['modified'], reverse=True)[:5]
            
            for file_info in recent_files:
                size_kb = file_info['size'] / 1024
                modified_str = file_info['modified'].strftime("%Y-%m-%d %H:%M:%S")
                print(f"   - {file_info['key']} ({size_kb:.1f} KB, {modified_str})")
            
            if len(folder_info['files']) > 5:
                print(f"   ... 他 {len(folder_info['files']) - 5} ファイル")
            print()
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ バケット '{bucket_name}' が見つかりません")
        elif error_code == '403':
            print(f"❌ バケット '{bucket_name}' へのアクセス権限がありません")
        else:
            print(f"❌ バケットアクセスエラー: {e}")
    except Exception as e:
        print(f"❌ バケット内容の取得に失敗: {e}")


def check_push_notification_icons(s3_client, bucket_name):
    """
    プッシュ通知アイコン用フォルダの確認
    """
    print("🔔 プッシュ通知アイコンフォルダの確認:")
    
    prefixes = [
        'media/push_notification_icons/',
        'push_notification_icons/',
        'media/'
    ]
    
    for prefix in prefixes:
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                MaxKeys=10
            )
            
            if 'Contents' in response:
                print(f"   ✅ {prefix} フォルダが存在します")
                print(f"      ファイル数: {len(response['Contents'])}")
                for obj in response['Contents']:
                    size_kb = obj['Size'] / 1024
                    print(f"      - {obj['Key']} ({size_kb:.1f} KB)")
            else:
                print(f"   ⚪ {prefix} フォルダは空です")
                
        except Exception as e:
            print(f"   ❌ {prefix} フォルダの確認に失敗: {e}")


def check_recent_uploads(s3_client, bucket_name, hours=24):
    """
    最近アップロードされたファイルを確認
    """
    print(f"⏰ 過去{hours}時間以内にアップロードされたファイル:")
    
    try:
        from datetime import timedelta
        cutoff_time = datetime.now().replace(tzinfo=None) - timedelta(hours=hours)
        
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            print("   ファイルが見つかりません")
            return
        
        recent_files = []
        for obj in response['Contents']:
            # タイムゾーン情報を削除して比較
            obj_time = obj['LastModified'].replace(tzinfo=None)
            if obj_time > cutoff_time:
                recent_files.append(obj)
        
        if not recent_files:
            print(f"   過去{hours}時間以内のアップロードはありません")
            return
        
        # 新しい順にソート
        recent_files.sort(key=lambda x: x['LastModified'], reverse=True)
        
        print(f"   {len(recent_files)}個のファイルが見つかりました:")
        for obj in recent_files:
            size_kb = obj['Size'] / 1024
            modified_str = obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S")
            print(f"   - {obj['Key']} ({size_kb:.1f} KB, {modified_str})")
            
    except Exception as e:
        print(f"❌ 最近のアップロードの確認に失敗: {e}")


def generate_presigned_urls(s3_client, bucket_name):
    """
    最新の画像ファイルの署名付きURLを生成
    """
    print("🔗 最新画像ファイルの署名付きURL:")
    
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            print("   画像ファイルが見つかりません")
            return
        
        # 画像ファイルのみをフィルタリング
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        image_files = []
        
        for obj in response['Contents']:
            key = obj['Key'].lower()
            if any(key.endswith(ext) for ext in image_extensions):
                image_files.append(obj)
        
        if not image_files:
            print("   画像ファイルが見つかりません")
            return
        
        # 最新の3ファイルを取得
        image_files.sort(key=lambda x: x['LastModified'], reverse=True)
        latest_images = image_files[:3]
        
        for obj in latest_images:
            try:
                # 署名付きURL生成（1時間有効）
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': obj['Key']},
                    ExpiresIn=3600
                )
                
                size_kb = obj['Size'] / 1024
                modified_str = obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S")
                print(f"   📸 {obj['Key']} ({size_kb:.1f} KB, {modified_str})")
                print(f"      URL: {url}")
                print()
                
            except Exception as e:
                print(f"   ❌ {obj['Key']} のURL生成に失敗: {e}")
                
    except Exception as e:
        print(f"❌ 署名付きURL生成に失敗: {e}")


def main():
    """
    メイン関数
    """
    print("=== S3バケット内容確認 ===\n")
    
    # .envファイルを読み込み
    if not load_env_file():
        return False
    
    # S3クライアントを取得
    s3_client = get_s3_client()
    if not s3_client:
        return False
    
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    if not bucket_name:
        print("❌ バケット名が設定されていません")
        return False
    
    print(f"🪣 バケット名: {bucket_name}")
    print(f"🌏 リージョン: {os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-1')}")
    print()
    
    # バケット内容の一覧表示
    list_all_objects(s3_client, bucket_name)
    
    # プッシュ通知アイコンフォルダの確認
    check_push_notification_icons(s3_client, bucket_name)
    print()
    
    # 最近のアップロードを確認
    check_recent_uploads(s3_client, bucket_name)
    print()
    
    # 署名付きURLを生成
    generate_presigned_urls(s3_client, bucket_name)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)