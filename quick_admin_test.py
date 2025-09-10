#!/usr/bin/env python3
"""
管理画面でのアップロードテスト結果を確認するクイックスクリプト
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Django設定をセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'handball_video_analysis.settings')
django.setup()

from notices.models import Notice
from django.conf import settings
import boto3


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


def check_django_notices():
    """
    Djangoデータベースのお知らせを確認
    """
    print("📊 Django データベースのお知らせ確認:")
    
    try:
        notices = Notice.objects.all().order_by('-created_at')
        
        if not notices.exists():
            print("   📭 お知らせが登録されていません")
            return
        
        print(f"   📋 登録済みお知らせ数: {notices.count()}")
        
        for i, notice in enumerate(notices[:5], 1):
            print(f"\n   {i}. {notice.title}")
            print(f"      ID: {notice.id}")
            print(f"      作成日時: {notice.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"      お知らせ区分: {notice.get_notice_type_display()}")
            print(f"      ステータス: {notice.get_status_display()}")
            
            # プッシュ通知アイコンの確認
            if notice.push_notification_icon:
                print(f"      🔔 プッシュ通知アイコン: {notice.push_notification_icon.name}")
                print(f"         URL: {notice.push_notification_icon.url}")
                
                # ファイルの存在確認
                try:
                    file_size = notice.push_notification_icon.size
                    print(f"         サイズ: {file_size / 1024:.1f} KB")
                except Exception as e:
                    print(f"         ⚠️ ファイルアクセスエラー: {e}")
            else:
                print(f"      📭 プッシュ通知アイコン: 未設定")
        
        if notices.count() > 5:
            print(f"\n   ... 他 {notices.count() - 5} 件")
            
    except Exception as e:
        print(f"❌ データベース確認エラー: {e}")


def check_s3_push_icons():
    """
    S3のプッシュ通知アイコンフォルダを確認
    """
    print(f"\n🔔 S3プッシュ通知アイコンフォルダ確認:")
    
    if not getattr(settings, 'USE_S3', False):
        print("   ℹ️ S3は無効です（ローカルファイルストレージを使用）")
        return
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        prefix = 'media/push_notification_icons/'
        
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix
        )
        
        if 'Contents' in response:
            print(f"   📁 {prefix} フォルダ:")
            for obj in response['Contents']:
                size_kb = obj['Size'] / 1024
                modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"      - {obj['Key']} ({size_kb:.1f} KB, {modified})")
                
                # 直接URLを生成
                region = settings.AWS_S3_REGION_NAME
                url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{obj['Key']}"
                print(f"        URL: {url}")
        else:
            print(f"   📭 {prefix} フォルダは空です")
            
    except Exception as e:
        print(f"❌ S3確認エラー: {e}")


def check_recent_activity():
    """
    最近の活動を確認
    """
    print(f"\n⏰ 最近の活動（過去1時間）:")
    
    try:
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_notices = Notice.objects.filter(
            created_at__gte=one_hour_ago
        ).order_by('-created_at')
        
        if recent_notices.exists():
            print(f"   🆕 新しいお知らせ: {recent_notices.count()}件")
            for notice in recent_notices:
                created_time = notice.created_at.strftime('%H:%M:%S')
                icon_status = "🔔" if notice.push_notification_icon else "📭"
                print(f"      {created_time} - {notice.title} {icon_status}")
        else:
            print(f"   📭 過去1時間以内の新しいお知らせはありません")
            
    except Exception as e:
        print(f"❌ 最近の活動確認エラー: {e}")


def show_test_instructions():
    """
    テスト手順を表示
    """
    print(f"\n🎯 管理画面でのアップロードテスト手順:")
    print(f"1. ブラウザで http://127.0.0.1:8000/admin/ にアクセス")
    print(f"2. admin / admin でログイン")
    print(f"3. 「お知らせ」→「追加」をクリック")
    print(f"4. 以下の情報を入力:")
    print(f"   - タイトル: 「アップロードテスト」")
    print(f"   - お知らせ区分: 任意選択")
    print(f"   - ステータス: 「下書き」")
    print(f"   - プッシュ通知アイコン: test_images/push_notification_icon_test.png")
    print(f"5. 「保存」をクリック")
    print(f"6. このスクリプトを再実行して結果を確認")
    
    print(f"\n📁 利用可能なテスト画像:")
    test_dir = "test_images"
    if os.path.exists(test_dir):
        for filename in os.listdir(test_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(test_dir, filename)
                file_size = os.path.getsize(file_path) / 1024
                print(f"   - {filename} ({file_size:.1f} KB)")
    else:
        print(f"   ⚠️ test_images フォルダが見つかりません")
        print(f"   python3 create_test_images.py を実行してください")


def main():
    """
    メイン関数
    """
    print("=== Django管理画面アップロードテスト確認 ===\n")
    
    # .envファイルを読み込み
    load_env_file()
    
    # 各種確認を実行
    check_django_notices()
    check_s3_push_icons()
    check_recent_activity()
    show_test_instructions()
    
    print(f"\n💡 このスクリプトを定期的に実行して、アップロード状況を確認してください")
    print(f"   python3 quick_admin_test.py")


if __name__ == "__main__":
    main()