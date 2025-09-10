#!/usr/bin/env python3
"""
S3へのアップロードを監視するスクリプト
管理画面でのアップロードテスト用
"""

import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import sys
import time
from datetime import datetime, timedelta


def load_env_file(env_path='.env'):
    """
    .envファイルを読み込んで環境変数に設定する
    """
    if not os.path.exists(env_path):
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


def get_current_files(s3_client, bucket_name):
    """
    現在のS3ファイル一覧を取得
    """
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            return {}
        
        files = {}
        for obj in response['Contents']:
            files[obj['Key']] = {
                'size': obj['Size'],
                'modified': obj['LastModified'],
                'etag': obj['ETag']
            }
        
        return files
        
    except Exception as e:
        print(f"❌ ファイル一覧の取得に失敗: {e}")
        return {}


def monitor_uploads(s3_client, bucket_name, duration_minutes=10):
    """
    指定時間、S3へのアップロードを監視
    """
    print(f"🔍 S3アップロード監視を開始します（{duration_minutes}分間）")
    print(f"📊 バケット: {bucket_name}")
    print("=" * 60)
    
    # 初期状態を取得
    initial_files = get_current_files(s3_client, bucket_name)
    print(f"📂 現在のファイル数: {len(initial_files)}")
    
    if initial_files:
        print("現在のファイル:")
        for key, info in list(initial_files.items())[:5]:  # 最大5件表示
            size_kb = info['size'] / 1024
            modified = info['modified'].strftime("%H:%M:%S")
            print(f"   - {key} ({size_kb:.1f} KB, {modified})")
        if len(initial_files) > 5:
            print(f"   ... 他 {len(initial_files) - 5} ファイル")
    
    print("\n👀 新しいアップロードを監視中...")
    print("   (Ctrl+C で終了)")
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    try:
        while datetime.now() < end_time:
            current_files = get_current_files(s3_client, bucket_name)
            
            # 新しいファイルを検出
            new_files = {}
            updated_files = {}
            
            for key, info in current_files.items():
                if key not in initial_files:
                    new_files[key] = info
                elif initial_files[key]['etag'] != info['etag']:
                    updated_files[key] = info
            
            # 新しいファイルを報告
            if new_files:
                print(f"\n🆕 新しいファイルが検出されました！ ({datetime.now().strftime('%H:%M:%S')})")
                for key, info in new_files.items():
                    size_kb = info['size'] / 1024
                    print(f"   ✅ {key} ({size_kb:.1f} KB)")
                    
                    # プッシュ通知アイコンかどうかチェック
                    if 'push_notification_icons' in key:
                        print(f"      🔔 プッシュ通知アイコンとして保存されました！")
                        
                        # URLを生成
                        region = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-1')
                        url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
                        print(f"      🌐 URL: {url}")
                        
                        # 署名付きURLも生成
                        try:
                            signed_url = s3_client.generate_presigned_url(
                                'get_object',
                                Params={'Bucket': bucket_name, 'Key': key},
                                ExpiresIn=3600
                            )
                            print(f"      🔗 署名付きURL (1時間有効): {signed_url}")
                        except Exception as e:
                            print(f"      ⚠️ 署名付きURL生成エラー: {e}")
                
                # 初期状態を更新
                initial_files.update(new_files)
            
            # 更新されたファイルを報告
            if updated_files:
                print(f"\n🔄 更新されたファイルが検出されました！ ({datetime.now().strftime('%H:%M:%S')})")
                for key, info in updated_files.items():
                    size_kb = info['size'] / 1024
                    print(f"   🔃 {key} ({size_kb:.1f} KB)")
                
                initial_files.update(updated_files)
            
            # 残り時間を表示
            remaining = end_time - datetime.now()
            remaining_minutes = int(remaining.total_seconds() / 60)
            remaining_seconds = int(remaining.total_seconds() % 60)
            
            if remaining_minutes > 0 or remaining_seconds > 0:
                print(f"\r⏰ 残り時間: {remaining_minutes:02d}:{remaining_seconds:02d}", end='', flush=True)
            
            time.sleep(5)  # 5秒間隔でチェック
    
    except KeyboardInterrupt:
        print(f"\n\n⏹️ 監視を停止しました")
    
    # 最終結果
    final_files = get_current_files(s3_client, bucket_name)
    new_count = len(final_files) - len(initial_files)
    
    print(f"\n📊 監視結果:")
    print(f"   開始時ファイル数: {len(initial_files)}")
    print(f"   終了時ファイル数: {len(final_files)}")
    print(f"   新規追加: {new_count} ファイル")
    
    if new_count > 0:
        print(f"\n🎉 管理画面からのアップロードが正常に動作しています！")
    else:
        print(f"\n💡 新しいアップロードは検出されませんでした")
        print(f"   管理画面でファイルをアップロードしてみてください")


def show_push_notification_icons(s3_client, bucket_name):
    """
    プッシュ通知アイコン専用フォルダの内容を表示
    """
    print(f"\n🔔 プッシュ通知アイコンフォルダの確認:")
    
    prefixes = [
        'media/push_notification_icons/',
        'push_notification_icons/',
    ]
    
    found_any = False
    
    for prefix in prefixes:
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                found_any = True
                print(f"   📁 {prefix}")
                for obj in response['Contents']:
                    size_kb = obj['Size'] / 1024
                    modified = obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S")
                    print(f"      - {obj['Key']} ({size_kb:.1f} KB, {modified})")
                    
        except Exception as e:
            print(f"   ❌ {prefix} の確認に失敗: {e}")
    
    if not found_any:
        print("   📭 プッシュ通知アイコンはまだアップロードされていません")


def main():
    """
    メイン関数
    """
    print("=== Django管理画面アップロード監視 ===\n")
    
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
    
    # 現在のプッシュ通知アイコンを表示
    show_push_notification_icons(s3_client, bucket_name)
    
    print(f"\n🎯 テスト手順:")
    print(f"1. ブラウザで http://127.0.0.1:8000/admin/ にアクセス")
    print(f"2. admin / admin でログイン")
    print(f"3. 「お知らせ」→「追加」をクリック")
    print(f"4. 基本情報を入力（タイトル、お知らせ区分など）")
    print(f"5. プッシュ通知アイコンに test_images/ の画像をアップロード")
    print(f"6. 保存ボタンをクリック")
    print(f"7. このスクリプトでアップロードを確認")
    
    input(f"\n📝 準備ができたら Enter キーを押してください...")
    
    # アップロードを監視
    monitor_uploads(s3_client, bucket_name, duration_minutes=10)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)